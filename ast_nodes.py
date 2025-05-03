class ASTNode: pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class Import(ASTNode):
    def __init__(self, module_path, alias):
        self.module_path = module_path
        self.alias = alias

class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class VarDecl(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Print(ASTNode):
    def __init__(self, args):
        self.args = args

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class Call(ASTNode):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

class Return(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOp(ASTNode):  # 新增二元运算节点
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right