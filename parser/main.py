import os
import sys
import keyword

# TOKEN CODE - jh
IDENTIFIER = 1
ASSIGN_OP = 2
ADD_OP = 3
SUB_OP = 4
MUL_OP = 5
DIV_OP = 6
SEMICOLON = 7
LEFT_PAREN = 8
RIGHT_PAREN = 9
CONSTANT = 10
EOF = -1

# global token - jh
next_token = None
token_string = ""
op_count = 0
errors = []
table = {}
paren = 0

# 각 연산자에 해당하는 변수 맵핑 - jh
op_map = {
    '+': ADD_OP,
    '-': SUB_OP,
    '*': MUL_OP,
    '/': DIV_OP
}

# 괄호, 세미콜론에 해당하는 변수 맵핑 - jh
pl_map = {
    ';': SEMICOLON,
    '(': LEFT_PAREN,
    ')': RIGHT_PAREN
}

# global table 초기화 및 table 참조 - jh
class SymbolTable:
    def __init__(self):
        global table
        table = {}
    def add_symbol(self, ident, value="Unknown"):
        global table
        table[ident] = value

    def get_symbol(self, ident):
        global table
        return table.get(ident)    # 식별자가 존재하지 않을 경우 "Unknown" 반환 - jh

class LexicalAnalysis:
    def __init__(self, input_text, symbol_table):
        global op_count, errors    # 구문분석 시 사용할 수 있도록 global로 - jh

        self.text = input_text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.symbol_table = symbol_table
        self.ident_count = 0
        self.const_count = 0
        op_count = 0
        errors = []
        self.read_line = []
        self.parse_success = True

    def advance(self):
        """현재 text의 길이를 넘지 않을 때까지"""
        global errors
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            if self.pos == len(self.text) - 1 and self.current_char != ';':    # 세미콜론 누락 확인
                errors.append("(Warning) ; 누락")
        else:
            self.current_char = None  

    def skip_whitespace(self):
        """빈 공간 건너뛰기 함수 종료 시 current_char는 빈 공간이 아닌 pos를 가리킴"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_number(self):
        num_str = ''
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        self.const_count += 1
        return CONSTANT, int(num_str)

    def get_identifier(self):
        global table, errors
        ident = ''
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit()):
            ident += self.current_char
            self.advance()
        if ident in keyword.kwlist:    # 예약어를 사용하였을 경우 error 발생
            errors.append("(Warning) 예약어가 사용되었음")
        
        self.ident_count += 1
        
        return IDENTIFIER, ident

    def lexical(self):
        """lexeme 얻기"""
        global op_count

        self.skip_whitespace()

        if self.current_char is None:
            return EOF, 'EOF'

        # 식별자 - jh
        if self.current_char.isalpha():  
            token_type, ident = self.get_identifier()
            self.read_line.append(ident)
            return token_type, ident

        # 상수 - jh
        elif self.current_char.isdigit():  
            token_type, number = self.get_number()
            self.read_line.append(str(number))
            return token_type, number
        
        # 연산자 - jh
        elif self.current_char in op_map:
            temp_char = self.current_char
            self.advance()
            self.read_line.append(temp_char)
            op_count += 1
            return op_map[temp_char], temp_char
        
        # 괄호 및 세미콜론 - jh
        elif self.current_char in pl_map:
            temp_char = self.current_char
            self.advance()
            self.read_line.append(temp_char)
            return pl_map[temp_char], temp_char

        # 할당 연산자 - jh
        elif self.current_char == ':':
            self.advance()
            if self.current_char == '=':
                self.advance()
                self.read_line.append(":=")
                return ASSIGN_OP, ':='
        
        elif self.current_char == '=':
            self.advance()
            self.read_line.append("=")
            return "=", "="

        else:
            return EOF, "EOF"


    # lexical을 통해 얻은 type과 string을 next_token, token_string에 저장 - jh
    def analyze(self):
        global next_token, token_string    # 구문분석 시 next_token으로 해당 token의 type을 비교 - jh

        next_token, token_string = self.lexical()


    def print_result(self):
        if self.read_line:
            print(" ".join(self.read_line))
            print(f"ID: {self.ident_count}; CONST: {self.const_count}; OP: {op_count};")
            if self.parse_success and not errors:
                print('(OK)')
            else:
                for error in errors:
                    print(f"{error}")
            print()  # 줄 구분을 위해 추가 - jh


# parser - ty, pass는 일단 에러 처리
# 작동규칙 self.analyze -> 다음 넌터미널 / 저거 끝나면 next_token이랑 token_string 리턴
class Parser:
    def __init__(self, lexer):
        global next_token, token_string

        self.lexer = lexer
        self.errors = errors
        self.lexer.analyze() # 첫 토큰 가져옴

    # <program> -> <statements>
    def program(self):
        global next_token, token_string

        if next_token == EOF:
            return
        self.statements()

    # <statements> -> <statement> | <statement><semi_colon><statements>
    def statements(self):
        global next_token, token_string

        if next_token == EOF: 
            return

        # -> <statement>
        self.statement()
        
        # -> <statement> -> <semi_colon>
        if next_token == SEMICOLON:
            self.lexer.analyze()
            if token_string == ";":
                errors.append("(Warning) 이중 세미콜론")
            self.statements()
        else:
            pass

    # <statement> -> <ident><assignment_op><expression>
    def statement(self):
        global next_token, token_string, errors
        
        # -> <ident>
        if next_token == IDENTIFIER:
            ident = token_string
            self.lexer.analyze()

            # -> <assignment_op>
            if next_token == ASSIGN_OP:
                self.lexer.analyze()
                if token_string == ";":
                    errors.append("(Error) := 뒤에 표현식이 없음")
                result = self.expression()
                global_symbol_table.add_symbol(ident, result)

            elif next_token == '=': # <assign_op> 존재 안함
                errors.append("(Warning) assign_op_error")
                self.lexer.analyze()
                result = self.expression()    # :이 생략된 경우 그냥 값이 할당할 수 있도록 함
                global_symbol_table.add_symbol(ident, result)
            
            elif token_string in op_map:    # ident 후 바로 연산자가 나오게 된 경우 
                temp_string = token_string
                self.lexer.analyze()
                if token_string == '=':
                    errors.append(f"(Error) := 나오기전 {temp_string} 바로 나옴 ")
                    errors.append("(Warning) assign_op_error")
                elif next_token == ASSIGN_OP:
                    errors.append(f"(Error) {temp_string} 이후에 ':=' 나옴")
                self.lexer.analyze()
                result = self.expression()
                global_symbol_table.add_symbol(ident, "Unknown")

                
        else: # <ident> 존재 안함
            errors.append("(Error) ident_error")
            self.lexer.analyze()
            
            
    # <expression> -> <term><term_tail>
    def expression(self):
        term = self.term()
        if term != "Unknown":
            result = self.term_tail(term)
        else:
            result = "Unknown"
            self.term_tail(term)
        return result
    
    # <term_tail> -> <add_op><term><term_tail> | E
    def term_tail(self, term):
        global next_token, token_string, errors, op_count
        term_tail_result = term
        # -> <add_op> : 덧셈연산실행
        if next_token == ADD_OP:
            self.lexer.analyze()

            if next_token == ADD_OP:
                errors.append('(Warning)\"중복 연산자(+) 제거\"')
                op_count -= 1
                self.lexer.analyze()
            

            t = self.term()
            
            if t != "Unknown" and type(t) != int:
                errors.append("(Error) (+)후 피연산자 누락")
                return "Unknown"
            self.term_tail(t) # 재귀

            if t != "Unknown" and term != "Unknown":
                term_tail_result = t + term
            else:
                return "Unknown"
        
        # -> <add_op> : 뺄셈연산실행
        elif next_token == SUB_OP:
            self.lexer.analyze()
            if next_token == SUB_OP:
                errors.append('(Warning)\"중복 연산자(-) 제거\"')
                op_count -= 1
                self.lexer.analyze()
            t = self.term()
            if t != "Unknown" and type(t) != int:
                errors.append("(Error) (-)후 피연산자 누락")
                return "Unknown"
            self.term_tail(t) # 재귀

            if t != "Unknown" and term != "Unknown":
                term_tail_result = term - t
            else:
                return "Unknown"
            
        elif next_token == CONSTANT or next_token == IDENTIFIER:
            errors.append("(Error) 연산자 (+, - *, /) 누락")
            return "Unknown"

        return term_tail_result


    
    # <term> -> <factor><factor_tail>
    def term(self):
        factor = self.factor()
        if factor != "Unknown":
            term_result = self.factor_tail(factor)
        else:
            term_result = "Unknown"
            self.factor_tail(factor)

        return term_result

    # <factor_tail> -> <mult_op><factor><factor_tail> | E
    def factor_tail(self, factor):
        global next_token, token_string, op_count

        factor_tail_result = factor

        # -> <mult_op> : 곱셈 연산
        if next_token == MUL_OP:
            self.lexer.analyze()
            if next_token == MUL_OP:
                errors.append('(Warning)\"중복 연산자(*) 제거\"')
                op_count -= 1
                self.lexer.analyze()

            f = self.factor()
            if f != "Unknown" and type(f) != int:
                errors.append("(Error) (*)후 피연산자 누락")
                return "Unknown"
            self.factor_tail(f) # 재귀

            if f != "Unknown" and factor != "Unknown":
                factor_tail_result = f * factor
            

        # -> <mult_op> : 나눗셈 연산
        elif next_token == DIV_OP:
            self.lexer.analyze()
            
            if next_token == DIV_OP:
                errors.append('(Warning)\"중복 연산자(/) 제거\"')
                op_count -= 1
                self.lexer.analyze()

            f = self.factor()
            if f != "Unknown" and type(f) != int:
                errors.append("(Error) (/)후 피연산자 누락")
                return "Unknown"
            self.factor_tail(f) # 재귀

            if f != "Unknown" and factor != "Unknown":
                factor_tail_result = factor / f


        return factor_tail_result



    # <factor> -> <left_paren><expression><right_paren> | <ident> | <const>
    def factor(self):
        global next_token, token_string, paren

        # -> <left_paren>
        if next_token == LEFT_PAREN:
            paren += 1
            self.lexer.analyze()
            factor_result = self.expression()
            if next_token == RIGHT_PAREN:
                self.lexer.analyze()
            else:
                errors.append("(Error) ')' 없음")
            
            # <expr>다시 리턴이니까
            return factor_result
        
        # -> <ident>
        elif next_token ==  IDENTIFIER:
            ident = self.ident()
            self.lexer.analyze() # 터미널까지 옴
            if next_token == RIGHT_PAREN:
                paren -= 1
                if paren < 0:
                    errors.append("(Error) '(' 없음")
                    self.lexer.analyze()
                    return "Unknown"
            return ident

        # -> <const>
        elif next_token == CONSTANT:
            const = self.const()
            self.lexer.analyze()
            if next_token == RIGHT_PAREN:
                paren -= 1
                if paren < 0:
                    errors.append("(Error) '(' 없음")
                    self.lexer.analyze()
                    return "Unknown"
            return const

        else: # 아무것도 없는 경우
            errors.append("(Error) 예상치 못함")
            self.lexer.analyze()


    # <const> -> any decimal numbers
    def const(self):
        global token_string
        const = token_string
        return int(const)

    # <ident> -> any names conforming to C identifier rules
    def ident(self):
        global token_string, errors

        if token_string not in table:
            errors.append(f'(Error)\"정의되지 않은 변수 ({token_string})가 참조됨\"')
            global_symbol_table.add_symbol(token_string) 


        ident = global_symbol_table.get_symbol(token_string)

        return ident

if __name__ == "__main__":
    args = sys.argv[1:]
    txt_files = [f for f in args if f.endswith('.txt')]
    
    for file_name in txt_files:
        global_symbol_table = SymbolTable()
        print(f"'{file_name}' 파일 실행")
        with open(file_name, 'r') as f:
            for line in f:
                paren = 0 # 괄호수 초기화 -ty
                line = line.strip() 
                if line == "":
                    continue # 빈줄 처리 - ty

                lexer = LexicalAnalysis(line, global_symbol_table) # line.strip() 위로 가져와서 공백 처리 - ty
                parser = Parser(lexer)
                parser.program()
                lexer.print_result()
        
        # 결과 처리 - 앞줄로 당김 - ty
        sorted_dict = sorted(table.items())  # 'table'이 SymbolTable의 속성이라고 가정
        print('Result ==> ', end='')
        for i in range(len(sorted_dict)):
            print(sorted_dict[i][0], ':', sorted_dict[i][1], end='')
            if i != (len(sorted_dict)-1):
                print('; ', end='')
        print("\n")