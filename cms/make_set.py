    def make_set(self,field_dict,queryset):
        q_regex = '[|&()" ]'

        for field_type, field in field_dict.items():
            if field:
                splited = list()
                quoteds = re.findall(r'"[^"]*"', field)
                if quoteds:
                    field_pos = 0          
                    for s in quoteds:
                        quo_pos = field.find(s)
                        splited.append(re.split(q_regex,field[field_pos:quo_pos])
                        splited.append(s)
                        field_pos = quo_pos
                print(splited)            
                operators_dict = dict()
                operators_dict = { i:x for i,x in enumerate(splited) if x == '&' or x == '|' or x == '(' or x == ')' }
                query_position = operator_keys_pos = 0
                operators_dict_keys = list(operators_dict.keys())
                dict_lenght = len(operators_dict_keys)

                if operators_dict_keys:
                    print("Tem operador")
                    print(operators_dict)
                    print(operators_dict_keys)
                    while operator_keys_pos < dict_lenght:
                        operator_position = operators_dict_keys[operator_keys_pos]
                        print(operator_position)
                        end_pos = operators_dict_keys[operator_keys_pos + 1] if operator_keys_pos + 1 < dict_lenght  else None
                        print(end_pos)
                        q_args_left = {'{0}__{1}'.format(field_type, 'icontains'):''.join(splited[query_position:operator_position])}
                        q_args_right = {'{0}__{1}'.format(field_type, 'icontains'):''.join(splited[operator_position + 1:end_pos])}
                
                        print(''.join(splited[query_position:operator_position]))
                        print(''.join(splited[operator_position + 1:end_pos]))
                        if operators_dict[operator_position] == 'OR':
                            print(queryset.filter(**q_args_left))
                            print(queryset.filter(**q_args_right))
                            queryset = queryset.filter(**q_args_left) | queryset.filter(**q_args_right)

                        elif operators_dict[operator_position] == 'AND':
                            print(queryset.filter(**q_args_left))
                            print(queryset.filter(**q_args_right))
                            queryset = queryset.filter(**q_args_left) & queryset.filter(**q_args_right)

                        query_position = operator_position + 1
                        operator_keys_pos += 1
                else:
                    q_args = {'{0}__{1}'.format(field_type, 'icontains'):field}
                    queryset = queryset.filter(**q_args)
                    print(queryset)
                    print(queryset)
        print(queryset)
        return(queryset)
