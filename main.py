import sys
import os
import argparse
import tempfile
import shutil
from lexer import Lexer
from parser import Parser
from C_generator import CCodeGenerator

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Lothon Compiler")
    parser.add_argument("input", help="Input .lo file")
    parser.add_argument("--gen-c", action="store_true", help="Generate C code only (no compilation)")
    parser.add_argument("-o", "--output", help="Output directory for generated C code")
    args = parser.parse_args()

    # 读取输入文件
    with open(args.input, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # 生成AST
    lexer = Lexer(code)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    
    # 确定输出目录
    output_dir = args.output if args.output else tempfile.mkdtemp(prefix="lothon_")
    
    # 生成C代码
    generator = CCodeGenerator(output_dir)
    generator.generate(ast)
    
    # 仅在未设置--gen-c时编译运行
    if not args.gen_c:
        compile_and_run(output_dir, generator, args)  # 传递 args 对象
    else:
        print(f"C code generated at: {output_dir}")

def compile_and_run(output_dir, generator, args):  # 新增 args 参数
    # 构建GCC命令
    runtime_c = os.path.join(output_dir, 'l_runtime.c')
    main_c = os.path.join(output_dir, 'main.c')
    modules = [os.path.join(output_dir, f'{m}.c') for m in generator.imports]
    
    executable = os.path.join(output_dir, 'program')
    cmd = [
        'gcc',
        main_c,
        runtime_c,
        *modules,
        '-o', executable,
        '-Wall',
        '-Werror'
    ]
    
    # 编译
    if os.system(' '.join(cmd)) == 0:
        os.system(executable)
    else:
        print("Compilation failed")
    
    # 清理临时目录（仅限非用户指定目录）
    if not args.output:  # 正确访问 args 对象
        shutil.rmtree(output_dir)

if __name__ == '__main__':
    main()