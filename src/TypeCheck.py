#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  Turquoise - VHDL linter and compilation toolchain
#  Copyright (c) 2020-2021: Turquoise team
#
#  File name: TypeCheck.py
#
#  Description: Implementation of typechecking functions
#
# -----------------------------------------------------------------------------
from .Messages import Error, Info

def tc_entity_component(_entity_dict, _component_list, _logger):
    """
    @brief Helper function. Typecheck component against entity declaration
    @param _entity_dict
    @param _component_list
    @param _logger Logger instance
    @return None
    """
    for component in _component_list:
        component_name, component_filename, parsed_component = component

        if component_name not in _entity_dict:
            err = Error('', component_filename, 'Component "' + component_name +
                        '" has not been declared.')
            _logger.add_log(err)

        else:
            entity_file_name = _entity_dict[component_name][0]
            entity_name, entity_generics, entity_ports = _entity_dict[component_name][1]
            comp_name, comp_generics, comp_ports = parsed_component

            if len(comp_generics) != len(entity_generics) or \
               len(comp_ports) != len(entity_ports) :
                err = Error('', component_filename, 'Component "' + component_name +
                            '" does not match declared entity "' + entity_name + '" @ "' +
                            entity_file_name + '"')
                _logger.add_log(err)

                info = Info('hint - check each signal in the component and its matching entity')
                _logger.add_log(info)

            # Compare generic signals against entity declaration
            for sig in comp_generics:
                if sig not in entity_generics:
                    err = Error('', component_filename, '\nGeneric signal "' + sig +
                                '" in component "' + comp_name + '"' +
                                '" is not declared in entity "' + entity_name + '" @ "' +
                                entity_file_name + '"')
                    _logger.add_log(err)
                
                elif comp_generics[sig] != entity_generics[sig]:
                    err = Error('', component_filename, '\nGeneric signal "' + sig +
                                '" in component "' + entity_name + '" has type "' + 
                                str(comp_generics[sig]) + ', but is declared to have type "' +
                                str(entity_generics[sig]) + '" in "' + entity_file_name + '"')
                    _logger.add_log(err)

            # Compare ports signals against entity declaration
            for sig in comp_ports:
                if sig not in entity_ports:
                    err = Error('', component_filename, '\nPort signal "' + sig +
                                '" in component "' + comp_name + '"' +
                                '" is not declared in entity "' + entity_name + '" @ "' +
                                entity_file_name + '"')
                    _logger.add_log(err)
                
                elif comp_ports[sig] != entity_ports[sig]:
                    err = Error('', component_filename, '\nPort signal "' + sig +
                                '" in component "' + entity_name + '" has type "' + 
                                str(comp_ports[sig][1]) + '" (' + comp_ports[sig][0] + ')' +
                                ', but is declared to have type "' +
                                str(entity_ports[sig][1]) + '" (' + entity_ports[sig][0] + ')'
                                + ' in "' + entity_file_name + '"')
                    _logger.add_log(err)