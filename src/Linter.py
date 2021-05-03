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
from .Messages import Error, Warning
from .Tokenize import Tokenize
from .Entity import parse_entity_component
from .TypeCheck import tc_entity_component

class Linter:

    def __init__(self, _filenames, _logger):
        self._filenames = _filenames
        self._logger = _logger

    def print_status(self):
        # @TODO: add more stats
        self._logger.print_logs_to_terminal()
        self._logger.print_logs_to_file()

    def lint(self):
        """ Perform linting on provided files """

        # Global states
        entity_dict = {}
        component_list = []

        # Lint through a list of files
        for f in self._filenames:
            tokenize = Tokenize(f)
            token_iter = tokenize.get_token_iter()

            try:
                for token in token_iter:
                    # Skip comment and linebreaks
                    if isinstance(token, (StartOfDocumentToken, EndOfDocumentToken,
                                  LinebreakToken, SpaceToken,
                                  IndentationToken, CommentToken)):
                        continue

                    # Parse entity
                    if token.Value.lower() == 'entity':
                        token_iter = chain([token], token_iter)
                        entity = parse_entity_component(token_iter, self._logger, f)

                        if entity is not None:
                            if entity[0] in entity_dict:
                                duplicated_entity_filename = entity_dict[entity[0]][0]
                                warn = Warning(token.Start, f,
                                               'Duplicated entity declaration found. ' +
                                               'Entity "' + entity[0] +
                                               '" was previously declared in "' +
                                               duplicated_entity_filename + '"')
                                self._logger.add_log(warn)
                            else:
                                entity_dict[entity[0]] = (f, entity)

                    # Parse component
                    elif token.Value.lower() == 'component':
                        token_iter = chain([token], token_iter)
                        component = parse_entity_component(token_iter, self._logger, f)

                        if component is not None:
                            component_list.append((component[0], f, component))

                    else:
                        print('TOKEN IS {}'.format(token))
                        continue

            except ParserException as ex:
                err = Error(token.Start, f, str(ex))
                self._logger.add_log(err)

            except NotImplementedError as ex:
                err = Error(token.Start, f, str(ex))
                self._logger.add_log(err)

        tc_entity_component(entity_dict, component_list, self._logger)