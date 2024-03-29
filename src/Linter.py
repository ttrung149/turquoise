#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: Linter.py
#
#  Description: Implementation of Linter class that performs linting on
#  provided files. Refer to README.md for supported features.
#
# -----------------------------------------------------------------------------
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, \
                               SpaceToken, LinebreakToken, CommentToken, \
                               IndentationToken
from pyVHDLParser.Base import ParserException
from itertools import chain
from .Messages import Error, Warning, pp
from .Tokenize import Tokenize
from .Entity import parse_entity_component
from .Architecture import parse_architecture
from .Signal import parse_signal
from .TypeCheck import tc_entity_component
from .UsedCheck import check_signal_assigned_not_declared, check_signal_declared_not_used

class Linter:

    def __init__(self, _filenames, _logger):
        self._filenames = _filenames
        self._logger = _logger

    def print_status(self):
        # @TODO: add more stats
        self._logger.print_logs_to_terminal()
        self._logger.print_logs_to_file()
        self._logger.print_status()


    def lint(self):
        """ Perform linting on provided files """

        # Global states
        entity_dict = {}
        architecture_dict = {}

        # Lint through a list of files
        for f in self._filenames:
            pp('info', 'Linting "' + f + '" ...')

            tokenize = Tokenize(f)
            token_iter = tokenize.get_token_iter()

            try:
                for token in token_iter:
                    # Skip comment and linebreaks
                    if isinstance(token, (StartOfDocumentToken, EndOfDocumentToken,
                                  LinebreakToken, SpaceToken,
                                  IndentationToken, CommentToken)):
                        continue

                    # Parse entity, add to global state
                    if token.Value.lower() == 'entity':
                        token_iter = chain([token], token_iter)
                        entity = parse_entity_component(token_iter, self._logger, f)

                        if entity is not None:
                            if entity.name in entity_dict:
                                duplicated_entity_filename = entity_dict[entity.name][0]
                                warn = Warning(token.Start, f,
                                               'Duplicated entity declaration found. ' +
                                               'Entity "' + entity.name +
                                               '" was previously declared in "' +
                                               duplicated_entity_filename + '"')
                                self._logger.add_log(warn)
                            else:
                                entity_dict[entity.name] = (f, entity)

                    # Parse architecture, add to global state
                    elif token.Value.lower() == 'architecture':
                        token_iter = chain([token], token_iter)
                        arch = parse_architecture(token_iter, self._logger, f)

                        if arch is not None:
                            if arch.entity_name in architecture_dict:
                                duplicated_arch_filename = arch_dict[arch.entity_name][0]
                                warn = Warning(token.Start, f,
                                               'Duplicated architecture declaration found. ' +
                                               'Archtecture for entity "' + arch.entity_name +
                                               '" was previously declared in "' +
                                               duplicated_arch_filename + '"')
                                self._logger.add_log(warn)
                            else:
                                architecture_dict[arch.entity_name] = (f, arch, token.Start)
                    else:
                        continue

            except ParserException as ex:
                err = Error(token.Start, f, str(ex))
                self._logger.add_log(err)

            except NotImplementedError as ex:
                err = Error(token.Start, f, str(ex))
                self._logger.add_log(err)

        # Architecture list iteration
        for arch_name in architecture_dict:
            filename, architecture, line = architecture_dict[arch_name]

            # Perform entity component typecheck
            # ----------------------------------
            component_list = architecture.declared_components
            tc_entity_component(entity_dict, component_list, filename, self._logger)

            # Perform assigned but not declared check
            # ---------------------------------------
            _declared = dict(architecture.declared_signals)
            if arch_name not in entity_dict:
                err = Error(line, filename,
                            'No matching entity found for architecture "' + arch_name + '"')
                self._logger.add_log(err)
            else:
                _, entity = entity_dict[arch_name]

                # Add generic signals to declared signal dict
                for sig in entity.generics:
                    if sig in _declared:
                        warn = Warning(line, filename, 'Re-declaration of signal "' + sig + '"')
                        self._logger.add_log(warn)
                    else:
                        _declared[sig] = entity.generics[sig].type

                # Add port signal to declared signals
                for sig in entity.ports:
                    if sig in _declared:
                        warn = Warning(line, filename, 'Re-declaration of signal "' + sig + '"')
                        self._logger.add_log(warn)
                    else:
                        _declared[sig] = entity.ports[sig].type

                _assigned = architecture.assigned_signals
                check_signal_assigned_not_declared(_declared, _assigned, filename, self._logger)

            # Perform declared but not used check
            # -----------------------------------
            check_signal_declared_not_used(architecture.declared_signals,
                                           architecture.body_tokens, filename, self._logger)