from ast_nodes import *
from runtime_generator import generate_runtime
import os
from lexer import TokenType
class CCodeGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.imports = set()
        self.functions = []
        generate_runtime(output_dir)
    
    def generate(self, ast):
        for stmt in ast.statements:
            if isinstance(stmt, Import):
                self.process_import(stmt)
            elif isinstance(stmt, FunctionDef):
                self.process_function(stmt)
        
        self.generate_module_files()
        self.generate_main(ast)
    
    def process_import(self, import_node):
        module_name = '_'.join(import_node.module_path)
        self.imports.add(module_name)
    
    def process_function(self, func_node):
        if '.' in func_node.name:
            module_part, func_name = func_node.name.split('.', 1)
            self.functions.append({
                'module': module_part,
                'name': func_name,
                'params': func_node.params,
                'body': func_node.body,
                'return_type': 'LObject*'
            })
        else:
            self.functions.append({
                'module': 'main',
                'name': func_node.name,
                'params': func_node.params,
                'body': func_node.body,
                'return_type': 'LObject*'
            })
    
    def generate_module_files(self):
        for module in self.imports:
            header_path = os.path.join(self.output_dir, f'{module}.h')
            source_path = os.path.join(self.output_dir, f'{module}.c')
            
            with open(header_path, 'w') as f:
                f.write(f'#ifndef {module.upper()}_H\n')
                f.write(f'#define {module.upper()}_H\n')
                f.write('#include "l_runtime.h"\n\n')
                for func in self.functions:
                    if func['module'] == module:
                        params = ', '.join([f'LObject* {p}' for p in func['params']])
                        f.write(f'LObject* {module}_{func["name"]}({params});\n')
                f.write('\n#endif\n')
            
            with open(source_path, 'w') as f:
                f.write(f'#include "{module}.h"\n\n')
                for func in self.functions:
                    if func['module'] == module:
                        params = ', '.join([f'LObject* {p}' for p in func['params']])
                        f.write(f'LObject* {module}_{func["name"]}({params}) {{\n')
                        for stmt in func['body']:
                            if isinstance(stmt, Return):
                                expr_code = self._generate_expr(stmt.value)
                                f.write(f'    return {expr_code};\n')
                            else:
                                code = self._generate_statement(stmt)
                                f.write(f'    {code}\n')
                        f.write('}\n\n')
    
    def generate_main(self, ast):
        main_path = os.path.join(self.output_dir, 'main.c')
        with open(main_path, 'w') as f:
            f.write('#include "l_runtime.h"\n')
            for module in self.imports:
                f.write(f'#include "{module}.h"\n')
            
            f.write('\nint main() {\n')
            
            declared_vars = set()
            for stmt in ast.statements:
                if isinstance(stmt, VarDecl):
                    if stmt.name in self.imports:
                        raise ValueError(f"变量名 '{stmt.name}' 与模块名冲突！")
                    if stmt.name in declared_vars:
                        raise ValueError(f"重复变量名 '{stmt.name}'")
                    declared_vars.add(stmt.name)
                    code = self._generate_var(stmt)
                    f.write(f'    {code}\n')
            
            for stmt in ast.statements:
                if isinstance(stmt, Print):
                    code = self._generate_print(stmt)
                    f.write(f'    {code}\n')
                elif isinstance(stmt, Call) and not isinstance(stmt.parent, FunctionDef):
                    code = f'{self._generate_expr(stmt)};'
                    f.write(f'    {code}\n')
            
            f.write('\n    // 清理内存\n')
            for var in declared_vars:
                f.write(f'    l_free({var});\n')
            
            f.write('    return 0;\n}\n')
    
    def _generate_var(self, node):
        if node.value:
            return f'LObject* {node.name} = {self._generate_expr(node.value)};'
        return f'LObject* {node.name};'
    
    def _generate_print(self, node):
        codes = []
        for arg in node.args:
            codes.append(f'l_print({self._generate_expr(arg)});')
        codes.append('l_newline();')
        return '\n    '.join(codes)
    
    def _generate_expr(self, expr):
        if isinstance(expr, Literal):
            if isinstance(expr.value, str):
                escaped = expr.value.replace('"', '\\"')
                return f'l_new_string("{escaped}")'
            elif isinstance(expr.value, int):
                return f'l_new_int({expr.value})'
            elif isinstance(expr.value, float):
                return f'l_new_float({expr.value})'
        elif isinstance(expr, Variable):
            return expr.name
        elif isinstance(expr, BinaryOp):
            left = self._generate_expr(expr.left)
            right = self._generate_expr(expr.right)
            if expr.op == TokenType.PLUS:
                return f'l_add({left}, {right})'
            elif expr.op == TokenType.MINUS:
                return f'l_sub({left}, {right})'
            elif expr.op == TokenType.MULT:
                return f'l_mul({left}, {right})'
            elif expr.op == TokenType.DIV:
                return f'l_div({left}, {right})'
            else:
                raise ValueError(f"不支持的运算符: {expr.op}")
        elif isinstance(expr, Call):
            if '.' in expr.func_name:
                module, func = expr.func_name.split('.', 1)
                args = ', '.join(self._generate_expr(arg) for arg in expr.args)
                return f'{module}_{func}({args})'
            else:
                args = ', '.join(self._generate_expr(arg) for arg in expr.args)
                return f'{expr.func_name}({args})'
        return 'NULL'
    
    def _generate_statement(self, stmt):
        if isinstance(stmt, VarDecl):
            return self._generate_var(stmt) + ';'
        elif isinstance(stmt, Print):
            return self._generate_print(stmt).replace('\n', ';\n    ') + ';'
        elif isinstance(stmt, Call):
            return self._generate_expr(stmt) + ';'
        return ';'