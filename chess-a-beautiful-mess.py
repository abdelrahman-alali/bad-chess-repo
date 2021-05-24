import copy, time
PIECES = {'♖': 'R', '♜': 'R', '♘': 'N', '♞': 'N', '♗': 'B', '♝': 'B',
          '♕': 'Q', '♛': 'Q', '♔': 'K', '♚': 'K', '♟': 'P', '♙': 'P'}


class Piece:
    GRADIENT = {'R': [0], 'B': [1, -1], 'N': [2, 0.5, -2, -0.5]}
    SIDE = {'white': ['♜', '♞', '♝', '♛', '♚', '♟'], 'black': ['♖', '♘', '♗', '♕', '♔', '♙']}

    def __init__(self, other, initial_coords, image):
        self.initial_coords = initial_coords
        self.image = image
        self.letter = PIECES[self.image]
        other.board[initial_coords[1]][initial_coords[0]] = self
        if self.image in Piece.SIDE['white']:
            self.side = 'white'
        else:
            self.side = 'black'
        

    def capturing_pieces(self, other, captured_piece):
        other.board[captured_piece.initial_coords[1]][captured_piece.initial_coords[0]] = self
        other.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
        del captured_piece
        return 'really true'

    def no_flying_diag(self, other, ending_coords, gradient):
        # c = y - mx
        c = self.initial_coords[1] - gradient * self.initial_coords[0]
        x = self.initial_coords[0]
        if x > ending_coords[0]:
            inc = -1
        else:
            inc = 1
        while x+inc != ending_coords[0]:
            x += inc
            y = c + gradient * x
            if other.board[y][x] != ' ':
                return other.board[y][x]
        return True

    def no_flying_horiz_vert(self, other, ending_coords):
        if self.initial_coords[0] == ending_coords[0]:
            val = 1
        else:
            val = 0
        var = self.initial_coords[val]
        if var < ending_coords[val]:
            inc = 1
        else:
            inc = -1
        while var+inc != ending_coords[val]:
            var += inc
            if val and other.board[var][ending_coords[0]] != ' ':
                return other.board[var][ending_coords[0]]
            elif not val and other.board[ending_coords[1]][var] != ' ':
                return other.board[ending_coords[1]][var]
        #     raise ValueError
        return True

    def __str__(self):
        return self.image

    def in_check_vert_horiz(self, other):
        if self.side == 'white':
            positive = 8
            negative = -1
        else:
            positive = -1
            negative = 8
        horizontal_positive = horizontal_negative = vertical_positive = vertical_negative = None
        vertical_negative = self.no_flying_horiz_vert(other, (self.initial_coords[0], negative))
        vertical_positive = self.no_flying_horiz_vert(other, (self.initial_coords[0], positive))
        horizontal_negative = self.no_flying_horiz_vert(other, (negative, self.initial_coords[1]))
        horizontal_positive = self.no_flying_horiz_vert(other, (positive, self.initial_coords[1]))

        lst = [horizontal_negative, horizontal_positive, vertical_negative, vertical_positive]
        lst = [val.initial_coords for val in lst if type(val).__name__ in ['Queen', 'Rook'] and val.side != self.side]
        # if any(lst, lambda x: type(x).__name__ in ['Queen', 'Rook']):
        # if len(lst) != 0 and any(lst, lambda x: x.side != self.side): # python is annoying
        #     print('BAD')
        if lst:
            return lst
        else:
            return False

    def in_check_diag(self, other):
        c = self.initial_coords[1] - -1 * self.initial_coords[0]
        x = 0
        y = c
        if y > 7:
            difference = y - 7
            y -= difference
            x = difference
        if (x, y) != self.initial_coords:
            piece1 = self.no_flying_diag(other, [x, y], -1)
        else:
            piece1 = self
        if piece1 == True:
            piece1 = other.board[y][x]

        x = 7
        c = self.initial_coords[1] - 1 * self.initial_coords[0]
        y = 1 * x + c
        if y > 7:
            difference = y - 7
            y = 7
            x -= difference
        if (x, y) != self.initial_coords:
            piece2 = self.no_flying_diag(other, [x, y], 1)
        else:
            piece2 = self
        if piece2 == True:
            piece2 = other.board[y][x]

        x = 7
        c = self.initial_coords[1] + self.initial_coords[0]
        y = c - x
        if y < 0:
            x += y
            y = 0
        if (x, y) != self.initial_coords:
            piece3 = self.no_flying_diag(other, [x, y], -1)
        else:
            piece3 = self
        if piece3 == True:
            piece3 = other.board[y][x]

        x = 0
        y = self.initial_coords[1] - self.initial_coords[0]
        if y < 0:
            x -= y
            y = 0
        if (x, y) != self.initial_coords:
            piece4 = self.no_flying_diag(other, [x, y], 1)
        else:
            piece4 = self
        if piece4 == True:
            piece4 = other.board[y][x]
        lst = [piece1, piece2, piece3, piece4]
        pieces_check = [piece.initial_coords for piece in lst if type(piece).__name__ in ['Queen', 'Bishop'] and piece.side != self.side]
        if pieces_check:
            return pieces_check
        else:
            return False

    def in_check_knight(self, other):
        valid_coords = []
        for gradient in Piece.GRADIENT['N'][:2]:
            x1 = ((5 / (gradient ** 2 + 1)) ** 0.5 + self.initial_coords[0])
            x2 = (-(5 / (gradient ** 2 + 1)) ** 0.5 + self.initial_coords[0])
            y1 = (5 - (x1 - self.initial_coords[0])** 2) ** 0.5 + self.initial_coords[1]
            y2 = -(5 - (x2 - self.initial_coords[0])** 2) ** 0.5 + self.initial_coords[1]
            x3 = x2
            y3 = y1
            x4 = x1
            y4 = y2

            coordinates = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            valid_coords.extend([(int(var1), int(var2)) for var1, var2 in coordinates if min(var1, var2) >= 0 and max(var1, var2) < 8])
        for x, y in valid_coords:
            if isinstance(other.board[y][x], Knight) and self.side != other.board[y][x].side:
                return (x, y)
        else:
            return False
    
    
    def in_check_pawns_horizontal(self, other, operation):
        lst = [self.initial_coords[0] - 1, self.initial_coords[0] + 1]
        y = self.initial_coords[1] + operation
        if y in range(8):
            for x in lst:
                if x in range(8):
                    piece = other.board[y][x]
                    if isinstance(piece, Pawn) and piece.side != self.side:
                        return (x, y)
            else:
                return False
    
    def in_check_pawns_diagonal(self, other, operation):
        y = self.initial_coords[1] + -operation
        y2 = self.initial_coords[1] + -operation * 2
        # print('Y!', y, y2)
        if y in range(8) and isinstance(other.board[y][self.initial_coords[0]], Pawn):
            return self.initial_coords[0], y
        elif y2 in range(8) and isinstance(other.board[y2][self.initial_coords[0]], Pawn) and y2 == other.board[y2][self.initial_coords[0]].start:
            return self.initial_coords[0], y2
        else:
            return False

    def in_check_pawns(self, other, m):
        if self.side == 'white':
            operation = -1
        else:
            operation = 1
        if m:
            return self.in_check_pawns_diagonal(other, operation)
        else:
            return self.in_check_pawns_horizontal(other, operation)

    def kings_avoid_conflict(self, other, ending_coords):
        if self.side == 'white':
            other_coords = other.black_king.initial_coords
        else:
            other_coords = other.white_king.initial_coords
        distance = ((ending_coords[0] - other_coords[0]) ** 2 + (ending_coords[1] - other_coords[1]) ** 2) ** 0.5
        if distance <= 2 ** (1/2):
            return other_coords
        else:
            return False

    def check_baton(self, other, look_checkmate=False, m=0):
        # return [func(other) for func in [self.in_check_pawns, self.in_check_knight, self.in_check_diag, self.in_check_vert_horiz]] 
        lst = [self.in_check_pawns(other, m), self.in_check_knight(other)]
        val1 = self.in_check_diag(other)
        val2 = self.in_check_vert_horiz(other)
        for val in [val1, val2]:
            if type(val).__name__ == 'list':
                lst.extend(val)
            else:
                lst.append(val)
        if isinstance(self, King) and not look_checkmate:
            lst.append(self.kings_avoid_conflict(other, self.initial_coords))
        return lst


class King(Piece):
    def __init__(self, other, initial_coords, image):
        Piece.__init__(self, other, initial_coords, image)
        self.castlable = True
    
    def castling(self, other, ending_coords):
        y = 0 if self.side == 'white' else 7
        try:
            if not (other.board[y][0].castlable and ending_coords[0] == 2 or other.board[y][7].castlable and ending_coords[0] == 6):
                return False
        except AttributeError:
            return False
        temp_board = Board()
        temp_board.board = copy.deepcopy(other.board)
        temp_coords = self.initial_coords
        returned = True
        # self.side = 'white' if self.side == 'black' else 'black'
        increment = 1 if ending_coords[0] == 6 else -1
        for x in range(temp_coords[0]+increment, ending_coords[0]+increment, increment):
            temp_board.board[y][x-increment].initial_coords = (x, y)
            if temp_board.board[y][x] == ' ' or x == temp_coords[0]:
                temp_board.board[y][x], temp_board.board[y][x-increment] = temp_board.board[y][x-increment], temp_board.board[y][x]
            else:
                # other.board = copy.deepcopy(temp_board)
                self.initial_coords = temp_coords
                print(other.board[y][x])
                returned = False
                break
            is_check = [val for val in temp_board.board[y][x].check_baton(other) if val]
            if is_check:
                # other.board = copy.deepcopy(temp_board)
                self.initial_coords = temp_coords
                returned = False
                break
        else:
            # other.board = copy.deepcopy(temp_board)
            print(ending_coords, self.initial_coords)
            val = 7 if ending_coords[0] == 6 else 0
            self.initial_coords = temp_coords
            other.board[y][ending_coords[0]-increment], other.board[y][val] = other.board[y][val], other.board[y][ending_coords[0]-increment]
            other.board[y][ending_coords[0]-increment].initial_coords = (ending_coords[0]-increment, y)

        return returned

    def move_validation(self, other, ending_coords):

        # if self.side == 'white':
        #     self = good_board.white_king
        # else:
        #     self = good_board.black_king
        # print(other.white_king == self)
        # print('the initial coords are:', self.initial_coords)
        if (self.side == 'white' and self.initial_coords == (4, 0) and ending_coords in [(2, 0), (6, 0)] or self.side == 'black' and self.initial_coords == (4, 7) and ending_coords in [(2, 7), (6, 7)]) and self.castlable:
            val =  self.castling(other, ending_coords)
            return val
        if abs(self.initial_coords[0] - ending_coords[0]) > 1 or abs(self.initial_coords[1] - ending_coords[1]) > 1:
            return False
        else:
            return True

    def checkmate(self, other):
        is_check = [val for val in self.check_baton(other, True) if val]
        if not is_check:
            return False
        threats = []
        for coordinate in is_check:
            threats.extend([val for val in other.board[coordinate[1]][coordinate[0]].check_baton(other) if val])
            if threats and len(is_check) < 2:
                return False

        temp_board = Board()
        temp_coords = tuple(self.initial_coords)
        coordinates = [(self.initial_coords[0] + 1, self.initial_coords[1]),
                       (self.initial_coords[0] - 1, self.initial_coords[1]),
                       (self.initial_coords[0], self.initial_coords[1] + 1),
                       (self.initial_coords[0], self.initial_coords[1] - 1),
                       (self.initial_coords[0] + 1, self.initial_coords[1] + 1),
                       (self.initial_coords[0] - 1, self.initial_coords[1] - 1),
                       (self.initial_coords[0] + 1, self.initial_coords[1] -1),
                       (self.initial_coords[0] - 1, self.initial_coords[1] + 1)]
        coordinates = [coordinate for coordinate in coordinates if max(coordinate) < 8 and min(coordinate) >= 0]
        for coordinate in coordinates:
            self.initial_coords = temp_coords
            temp_board.board = copy.deepcopy(other.board)
            if temp_board.board[coordinate[1]][coordinate[0]] == ' ' or temp_board.board[coordinate[1]][coordinate[0]] != ' ' and temp_board.board[coordinate[1]][coordinate[0]].image not in Piece.SIDE[self.side]:
                if temp_board.board[coordinate[1]][coordinate[0]] == ' ':
                    temp_board.board[temp_coords[1]][temp_coords[0]], temp_board.board[coordinate[1]][coordinate[0]] = temp_board.board[coordinate[1]][coordinate[0]], temp_board.board[temp_coords[1]][temp_coords[0]]
                else:
                    temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
                    temp_board.board[coordinate[1]][coordinate[0]] = self
                self.initial_coords = coordinate
                is_mate = self.check_baton(temp_board)
                if not any(is_mate) and len(is_mate) > 0:
                    self.initial_coords = temp_coords
                    return False
        
        if len(is_check) > 1:
            self.initial_coords = temp_coords
            return True
        
        temp_side = self.side
        self.side = 'black' if self.side == 'white' else 'white'
        for coords in is_check:
            temp_board.board = copy.deepcopy(other.board)
            self.initial_coords = temp_coords
            try:
                m = int((self.initial_coords[1] - coords[1]) / (self.initial_coords[0] - coords[0]))
            except ZeroDivisionError:
                m = 0
            c = self.initial_coords[1] - m * self.initial_coords[0]
            increment = 1 if coords[0] > temp_coords[0] else -1
            
            if m in Piece.GRADIENT['B']:
                for x in range(temp_coords[0]+increment, coords[0], increment):
                    y = m * x + c
                    self.initial_coords = (x, y)
                    if temp_board.board[y][x] == ' ':
                        temp_board.board[y][x], temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = temp_board.board[self.initial_coords[1]][self.initial_coords[0]], temp_board.board[y][x]                    
                    elif temp_board.board[y][x].side != self.side:
                        temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
                        temp_board.board[y][x] = self
                    can_block = [val for val in self.check_baton(temp_board, True, m=m) if val]
                    if can_block:
                        is_check.remove(coords)
                        break
            elif m == 0 and self.initial_coords[0] - coords[0] == 0:
                for y in range(temp_coords[1] + increment, coords[1], increment):
                    x = self.initial_coords[0]
                    self.initial_coords = x, y
                    if temp_board.board[y][x] == ' ':
                        temp_board.board[y][x], temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = temp_board.board[self.initial_coords[1]][self.initial_coords[0]], temp_board.board[y][x]                    
                    elif temp_board.board[y][x].side != self.side:
                        temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
                        temp_board.board[y][x] = self
                    can_block = [val for val in self.check_baton(temp_board, True) if val]
                    if can_block:
                        is_check.remove(coords)
                        break
            elif m == 0:
                for x in range(self.initial_coords[0] + increment, coords[0], increment):
                    y = temp_coords[1]
                    self.initial_coords = x, y
                    if temp_board.board[y][x] == ' ':
                        temp_board.board[y][x], temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = temp_board.board[self.initial_coords[1]][self.initial_coords[0]], temp_board.board[y][x]                    
                    elif temp_board.board[y][x].side != self.side:
                        temp_board.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
                        temp_board.board[y][x] = self
                    can_block = [val for val in self.check_baton(temp_board, True) if val]
                    if can_block:
                        is_check.remove(coords)
                        break

        self.side = temp_side
        self.initial_coords = temp_coords
        if is_check:
            return True
        else:
            return False

                               

class Queen(Piece):

    def move_validation(self, other, ending_coords):
        try:
            gradient = (self.initial_coords[1] - ending_coords[1]) / (self.initial_coords[0] - ending_coords[0])
            if gradient in Piece.GRADIENT['R']:
                return isinstance(self.no_flying_horiz_vert(other, ending_coords), bool)
            elif gradient in Piece.GRADIENT['B']:
                return isinstance(self.no_flying_diag(other, ending_coords, int(gradient)), bool)
            else:
                return False
        except ZeroDivisionError:
            return isinstance(self.no_flying_horiz_vert(other, ending_coords), bool)


class Knight(Piece):

    def __init__(self, other, initial_coords, image):
        Piece.__init__(self, other, initial_coords, image)
        self.distance = 5 ** (1/2)

    def move_validation(self, ending_coords):
        try:
            gradient = (self.initial_coords[1] - ending_coords[1]) / (self.initial_coords[0] - ending_coords[0])
            distance = ((self.initial_coords[1] - ending_coords[1]) ** 2 + (self.initial_coords[0] - ending_coords[0]) ** 2) ** 0.5
            if gradient in Piece.GRADIENT[self.letter] and distance == self.distance:
                return True
            else:
                return False
        except ZeroDivisionError:
            return False


class Pawn(Piece):

    def __init__(self, other, initial_coords, image):
        Piece.__init__(self, other, initial_coords, image)
        if self.side == 'white':
            self.direction = 1
            self.start = 1
            self.end = 7
        else:
            self.direction = -1
            self.start = 6
            self.end = 0
        self.en_passantable = False

    def move_validation(self, other, ending_coords):
        end_location = other.board[ending_coords[1]][ending_coords[0]]
        difference_y = ending_coords[1] - self.initial_coords[1]
        difference_x = ending_coords[0] - self.initial_coords[0]
        if difference_x == 0 and (difference_y == 1 * self.direction or self.initial_coords[1] == self.start and difference_y == 2 * self.direction and other.board[ending_coords[1] - self.direction][ending_coords[0]] == ' ') and end_location == ' ':
            if difference_y == 2*self.direction:
                self.en_passantable = counter
            return True
        
        if abs(difference_x) == 1 and difference_y == self.direction and end_location != ' ':
            return self.capturing_pieces(other, end_location)
        else:
            return self.en_passant(other, ending_coords)
        
    def en_passant(self, other, ending_coords):
        the_beautiful_pawn_that_will_pass_away = other.board[self.initial_coords[1]][ending_coords[0]]
        if not isinstance(the_beautiful_pawn_that_will_pass_away, Pawn):
            return False
        end_location = other.board[ending_coords[1]][ending_coords[0]]
        if abs(self.initial_coords[0] - ending_coords[0]) == 1 and abs(self.initial_coords[1] - ending_coords[1]) == 1 and end_location == ' ' and counter - the_beautiful_pawn_that_will_pass_away.en_passantable == 1 and the_beautiful_pawn_that_will_pass_away.side != self.side:
            other.board[ending_coords[1]][ending_coords[0]] = self
            other.board[self.initial_coords[1]][self.initial_coords[0]] = ' '
            other.board[self.initial_coords[1]][ending_coords[0]] = ' '
            del the_beautiful_pawn_that_will_pass_away
            return 'really true'


class Rook(Piece):
    def __init__(self, other, initial_coords, image):
        Piece.__init__(self, other, initial_coords, image)
        self.castlable = True
    def move_validation(self, other, ending_coords):
        try:
            gradient = (self.initial_coords[1] - ending_coords[1]) / (self.initial_coords[0] - ending_coords[0])
            if gradient in Piece.GRADIENT[self.letter]:
                return isinstance(self.no_flying_horiz_vert(other, ending_coords), bool)
            else:
                return False
        except ZeroDivisionError:
            return isinstance(self.no_flying_horiz_vert(other, ending_coords), bool)
        return False


class Bishop(Piece):

    def move_validation(self, other, ending_coords):
        try:
            gradient = (self.initial_coords[1] - ending_coords[1]) / (self.initial_coords[0] - ending_coords[0])
            if gradient in Piece.GRADIENT[self.letter]:
                return isinstance(self.no_flying_diag(other, ending_coords, int(gradient)), bool)
        except ZeroDivisionError:
            return False
        return False


class Board:

    def __init__(self):
        self.board = [[' '] * 8 for _ in range(8)]

        self.right_white_rook = Rook(self, (7, 0), '♜')
        self.left_white_rook = Rook(self, (0, 0), '♜')
        self.left_black_rook = Rook(self, (0, 7), '♖')
        self.right_black_rook = Rook(self, (7, 7), '♖')

        self.right_white_knight = Knight(self, (6, 0), '♞')
        self.left_white_knight = Knight(self, (1, 0), '♞')
        self.right_black_knight = Knight(self, (6, 7), '♘')
        self.left_black_knight = Knight(self, (1, 7), '♘')

        self.right_white_bishop = Bishop(self, (5, 0), '♝')
        self.left_white_bishop = Bishop(self, (2, 0), '♝')
        self.left_black_bishop = Bishop(self, (2, 7), '♗')
        self.right_black_bishop = Bishop(self, (5, 7), '♗')

        self.white_queen = Queen(self, (3, 0), '♛')
        self.black_queen = Queen(self, (3, 7), '♕')

        self.white_king = King(self, (4, 0), '♚')
        self.black_king = King(self, (4, 7), '♔')

        self.white_pawn_1 = Pawn(self, (0, 1), '♟')
        self.white_pawn_2 = Pawn(self, (1, 1), '♟')
        self.white_pawn_3 = Pawn(self, (2, 1), '♟')
        self.white_pawn_4 = Pawn(self, (3, 1), '♟')
        self.white_pawn_5 = Pawn(self, (4, 1), '♟')
        self.white_pawn_6 = Pawn(self, (5, 1), '♟')
        self.white_pawn_7 = Pawn(self, (6, 1), '♟')
        self.white_pawn_8 = Pawn(self, (7, 1), '♟')

        self.black_pawn_1 = Pawn(self, (0, 6), '♙')
        self.black_pawn_2 = Pawn(self, (1, 6), '♙')
        self.black_pawn_3 = Pawn(self, (2, 6), '♙')
        self.black_pawn_4 = Pawn(self, (3, 6), '♙')
        self.black_pawn_5 = Pawn(self, (4, 6), '♙')
        self.black_pawn_6 = Pawn(self, (5, 6), '♙')
        self.black_pawn_7 = Pawn(self, (6, 6), '♙')
        self.black_pawn_8 = Pawn(self, (7, 6), '♙')

    def display(self):
        print(' ', end=' ')
        print(*[chr(i + 65) for i in range(8)], sep=' |')
        for i in range(1, 9):
            print('_' * 25)
            print(i, end='|')
            print(*self.board[i-1], sep=' |')

    def syntax_validation(self, coords):
        try:
            starting_coords, ending_coords = coords.split()
        except ValueError:
            return False
        if len(starting_coords + ending_coords) != 4 or starting_coords == ending_coords:
            return False
        return starting_coords, ending_coords

    def coordinates_validation(self, starting_coords, ending_coords):
        starting_coords = (ord(starting_coords[0]) - ord('A'), int(starting_coords[1]) - 1)
        ending_coords = (ord(ending_coords[0]) - ord('A'), int(ending_coords[1]) - 1)

        try:
            if min(starting_coords[1], ending_coords[1]) < 0:
                raise IndexError
            piece = self.board[starting_coords[1]][starting_coords[0]]
            self.board[ending_coords[1]][ending_coords[0]]
        except IndexError:
            return False
        if piece == ' ':
            return False
        else:
            return piece, starting_coords, ending_coords

    def moving_pieces(self, ending_coords, piece):
        if self.board[ending_coords[1]][ending_coords[0]] == ' ':
            self.board[piece.initial_coords[1]][piece.initial_coords[0]], self.board[ending_coords[1]][ending_coords[0]] = self.board[ending_coords[1]][ending_coords[0]], self.board[piece.initial_coords[1]][piece.initial_coords[0]]
            return True
        elif self.board[ending_coords[1]][ending_coords[0]].side == piece.side:
            return False
        elif not isinstance(piece, Pawn):
            return piece.capturing_pieces(self, self.board[ending_coords[1]][ending_coords[0]])
        else:
            return piece.move_validation(self, ending_coords)

    def good_baton(self, turn):
        is_checkmate = False
        check_white, check_black = False, False
        prev_board = copy.deepcopy(self.board)
        while True:
            self.display()
            coords = input('Please enter the piece\'s starting position and its ending position in the following syntax: D2 D4. ')
            result = self.syntax_validation(coords)
            if result:
                starting_coords, ending_coords = result
            else:
                print('Invalid syntax')
                continue
            result = self.coordinates_validation(starting_coords, ending_coords)
            if result:
                piece, starting_coords, ending_coords = result
            else:
                print('Invalid input')
                continue
            if piece.side != turn:
                print('This isn\'t your turn')
                continue
            if not isinstance(piece, Knight):
                result = piece.move_validation(self, ending_coords)
            else:
                result = piece.move_validation(ending_coords)
            if not result:
                print('Incorrect move')
                continue
            if result != 'really true':
                result = self.moving_pieces(ending_coords, piece)
            if not result:
                print('Invalid move')
                continue
            if isinstance(piece, King) and abs(ending_coords[0] - starting_coords[0]) != 2:
                if piece.side == 'white':
                    self.white_king = piece
                elif piece.side == 'black' and piece.castlable == self.black_king.castlable:
                    self.black_king = piece
            piece.initial_coords = ending_coords
            if isinstance(piece, Pawn):
                if piece.initial_coords[1] == piece.end:
                    print('Your pawn can be promoted! Please pick one of the following pieces:')
                    print(*CHOICES, sep=', ')
                    choice = input()
                    while choice not in CHOICES:
                        choice = input('Invalid choice.')
                    if piece.side == 'white':
                        piece = [Rook(self, piece.initial_coords, '♜'), Queen(self, piece.initial_coords, '♛'), Knight(self, piece.initial_coords, '♞'), Bishop(self, piece.initial_coords, '♝')][CHOICES.index(choice)]    
                    else:
                        piece = [Rook(self, piece.initial_coords, '♖'), Queen(self, piece.initial_coords, '♕'), Knight(self, piece.initial_coords, '♘'), Bishop(self, piece.initial_coords, '♗')][CHOICES.index(choice)]   
                    self.board[piece.initial_coords[1]][piece.initial_coords[0]] = piece
            is_check = self.white_king.check_baton(self)
            check_white = True if any(is_check) else False
            is_check = self.black_king.check_baton(self)
            check_black = True if any(is_check) else False

            # print(turn, check_black, check_white)
            if turn == 'white' and check_black:
                is_checkmate = (self.black_king.checkmate(self))
            elif turn == 'black' and check_white:
                # print('turn is black and check_wihtie is true')
                is_checkmate = (self.white_king.checkmate(self))
            # print('is_checkmate is:', is_checkmate)
            if is_checkmate:
                return is_checkmate
            if check_white and turn == 'white' or check_black and turn == 'black':
                print('Invalid move, please prioritize the safety of your king to win')
                self.board = copy.deepcopy(prev_board)
                piece.initial_coords = starting_coords
                continue
            if type(piece).__name__ in ['Rook', 'King']:
                piece.castlable = False
                piece.initial_coords = ending_coords
            return is_checkmate

good_board = Board()
counter = 0
CHOICES = ['Rook', 'Queen', 'Knight', 'Bishop']
check_black, check_white = False, False

try:
    while True:
        turn = 'black' if counter % 2 else 'white'
        is_checkmate = good_board.good_baton(turn)
        # print('the white king is at', good_board.white_king.initial_coords)
        if is_checkmate:
            print(turn, 'wins! :)')
            break
        counter += 1
        time.sleep(0.5)
        print('\n' * 10)
        if check_white or check_black:
            print('check')
        print('This has not crashed yet.')
except:
    print('it crashed again :)')
