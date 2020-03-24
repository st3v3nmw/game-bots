from random import random
import simplejson as json
from copy import deepcopy
from urllib.request import urlopen, Request
from hashlib import sha1
from time import sleep, time

class Trie:
    class Node:
        def __init__(self):
            self.children = {}
            self.word_finished = False
            self.is_word = False

    def __init__(self, path):
        self.root = self.Node()
        with open(path, 'r') as f:
            wordlist = f.readlines()
            for word in wordlist:
                self.add(word.strip())
        self.words = []  # store results

    def add(self, word):
        node = self.root
        length = len(word)
        for i in range(length):
            char = word[i]
            if char in node.children:
                node = node.children[char]
            else:
                new_node = self.Node()
                node.children[char] = new_node
                node = new_node
            if length - 1 == i: node.is_word = True
        node.word_finished = True

    def query(self, q, letters):
        n_spaces = q.count('_')
        self.words = []
        self.getPartWord(self.root, q, letters, n_spaces, 0, "")
        return self.words

    def getPartWord(self, node, q, letters, n_spaces, position, word):
        if position == len(q):
            if node.is_word:
                self.words.append(word)
            return
        if q[position] == '_':
            for char in letters.keys():
                if letters[char] and char in node.children:
                    toPass = deepcopy(letters)
                    toPass[char] -= 1
                    self.getPartWord(node.children[char], q, toPass, n_spaces - 1, position + 1, word + char)
        else:
            for char in node.children.keys():
                if q[position] == char:
                    self.getPartWord(node.children[char], q, deepcopy(letters), n_spaces, position + 1, word + char)

    def verifyWord(self, word):
        node = self.root
        for position in range(len(word)):
            if word[position] in node.children:
                node = node.children[word[position]]
            else: return False
        return node.is_word

class Board:
    points = {"A": 1, "B": 4, "C": 4, "D": 2, "E": 1, "F": 4, "G": 3, "H": 4, "I": 1, "J": 10, "K": 5, "L": 1, "M": 3, "N": 1, "O": 1, "P": 4, "Q": 10, "R": 1, "S": 1, "T": 1, "U": 2, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10}
    empty_board = [['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'], ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_']]
    special_cells = {0: { 0: "TL", 14: "TL", 210: "TL", 224: "TL", 4: "TW", 7: "DL", 10: "TW", 16: "DL", 20: "TL", 60: "TW", 105: "DL", 150: "TW", 76: "TL", 136: "TL", 92: "DL", 122: "DL", 108: "DW", 94: "DL", 124: "DL", 154: "DW", 36: "DL", 66: "DL", 156: "DL", 217: "DL", 188: "DL", 204: "TL", 56: "TL", 164: "TW", 192: "DW", 132: "DL", 52: "DW", 80: "TL", 196: "DL", 182: "DW", 168: "TL", 214: "TW", 200: "TL", 160: "DW", 119: "DL", 32: "DW", 48: "TL", 64: "DW", 140: "TL", 172: "DW", 186: "DL", 220: "TW", 158: "DL", 144: "TL", 176: "TL", 208: "DL", 130: "DL", 116: "DW", 148: "TL", 100: "DL", 102: "DL", 84: "TL", 68: "DL", 70: "DW", 42: "DW", 28: "DL", 88: "TL", 74: "TW", 38: "DL", 24: "TL"}}
    # count = {"A": 10, "B": 2, "C": 2, "D": 5, "E": 12, "F": 2, "G": 3, "H": 3, "I": 9, "J": 1, "K": 1, "L": 4, "M": 2, "N": 6, "O": 7, "P": 2, "Q": 1, "R": 6, "S": 5, "T": 7, "U": 4, "V": 2, "W": 2, "X": 1, "Y": 2, "Z": 1}

    def __init__(self, game):
        self.gameId = game['id']
        self.board = deepcopy(self.empty_board)
        self.letters = {}
        # self.letter_count = deepcopy(self.count)
        self.save_rack(game)
        self.boardId = 0
        self.move_count = game['move_count']

    def load_board(self, tiles):
        for tile in tiles:
            self.board[tile[1]][tile[0]] = tile[2]
            # if not tile[3]: self.letter_count[tile[2]] -= 1

    def save_rack(self, game):
        local = 0 if game['players'][0]['is_local'] else 1
        self.opponent = game['players'][abs(1 - local)]['username']
        for letter in game['players'][local]['rack']:
            if letter in self.letters:
                self.letters[letter] += 1
            else:
                self.letters[letter] = 1
            # if letter != '': self.letter_count[letter] -= 1

class Bot:
    def __init__(self, email, password):
        print("WordFeud Bot\n============")
        self.trie = Trie("app/FILTERED.txt")
        self.twl06 = Trie("app/TWL06.txt")
        self.sessionId = None
        self.login(email, password)
        self.n_boards = 0
        self.boards = []
        self.loop()

    def query(self, q, letters):
        return self.trie.query(q, letters)

    def execute(self, url, data = {}):
        headers = {'content-type': 'application/json'}
        if self.sessionId:
            headers['Cookie'] = "sessionid=" + self.sessionId
        req = Request("http://game06.wordfeud.com/wf/" + url + '/', json.dumps(data).encode('utf-8'), headers=headers)
        r = urlopen(req)
        result = json.loads(r.read().decode('utf-8'))
        cookie = r.getheader('Set-Cookie')
        if cookie:
            idx_start, idx_end = cookie.index('=') + 1, cookie.index(';')
            self.sessionId = cookie[idx_start: idx_end]
        return result

    def login(self, email, password):
        password = password + "JarJarBinks9"
        password = sha1(password.encode('utf-8'))
        print("Attempting login...")
        result = self.execute('user/login/email', {'email': email, 'password': password.hexdigest()})
        if self.sessionId:
            print("Logged in as %s" % result['content']['username'])
        else:
            print("Login Failed")
            exit()

    def inviteRandom(self, boardtype):
        self.execute('random_request/create', {'ruleset': 0, 'board_type': boardtype})

    def get_games(self):
        print("Fetching games...")
        self.boards = []
        self.n_boards = 0
        result = self.execute('user/games')['content']['games']
        for game in result:
            if game['is_running']:
                self.n_boards += 1
                local = 0 if game['players'][0]['is_local'] else 1
                if game['current_player'] == local:
                    board = Board(game)
                    result = self.get_game(board.gameId)['game']
                    # board.endgame = result['bag_count'] == 0
                    board.boardId = result['board']
                    if board.boardId not in Board.special_cells:
                        self.get_special_cells(board.boardId)
                    board.load_board(result['tiles'])
                    self.boards.append(board)
        self.boards.reverse()

    def get_game(self, gameID):
        return self.execute('game/' + str(gameID))['content']

    def get_special_cells(self, boardID):
        b = {2: "TL", 1: "DL", 4: "TW", 3: "DW"}
        result = self.execute('board/' + str(boardID))['content']['board']
        special_cells = {}
        for i in range(15):
            for j in range(15):
                if result[i][j]:
                    special_cells[i * 15 + j] = b[result[i][j]]
        Board.special_cells[boardID] = special_cells

    def passRound(self, gameId):
        return self.execute('game/' + str(gameId) + '/pass')

    def place(self, gameId, tiles, words):
        return self.execute('game/' + str(gameId) + '/move', {'move': tiles, 'ruleset': 0, 'words': words})

    def swap(self, gameId, tiles):
        return self.execute('game/' + str(gameId) + '/swap', {'tiles': tiles})

    def acceptInvite(self, inviteId):
        self.execute('invite/' + str(inviteId) + '/accept')

    def rejectInvite(self, inviteId):
        self.execute('invite/' + str(inviteId) + '/reject')

    def getStatus(self):
        result = self.execute('user/status')['content']
        for invite in result['invites_received']:
            if invite['ruleset'] == 0:
                self.acceptInvite(invite['id'])
            else:
                self.rejectInvite(invite['id'])
        n = self.n_boards + len(result['invites_sent'])
        print(self.n_boards, len(self.boards))
        if n < 18:
            for _ in range(3):
                r = random()
                if r <= 0.5000: self.inviteRandom('normal')
                else: self.inviteRandom('random')

    def get_best_moves(self, board, letters, boardId, reverse_sort = True):
        wordset, done, built = set(), set(), set()
        # horizontal
        for k in range(15):
            row = board[k]
            idxs = [1] if k == 0 else [13] if k == 14 else [k-1, k+1]
            neighbours = []
            for idx in idxs:
                neighbours.append(board[idx])
            wordset.update(getPartWords(row, k, neighbours))
        # vertical
        for k in range(15):
            column = [board[i][k] for i in range(15)]
            idxs = [1] if k == 0 else [13] if k == 14 else [k-1, k+1]
            neighbours = []
            for idx in idxs:
                neighbours.append([board[i][idx] for i in range(15)])
            wordset.update(getPartWords(column, k, neighbours, False))

        for word, start, horizontal, sp , bingo in wordset:
            seq = self.query(word, letters)
            for x in seq:
                built.add((x, start, horizontal, sp, bingo))

        for word in built:
            points, correct = self.calculate_points(deepcopy(board), word, boardId)
            if correct: done.add((points, word))

        done = sorted(done, key=lambda x: x[0], reverse = reverse_sort)
        return done

    def get_first_moves(self, letters, boardId):
        words_mv = []
        for char in letters.keys():
            board = deepcopy(Board.empty_board)
            letters_copy = deepcopy(letters)
            letters_copy[char] -= 1
            board[7][7] = char
            if boardId:
                words_mv.extend(self.get_best_moves(board, letters_copy, boardId)[:25])
            else:
                words_mv.extend(self.get_best_moves(board, letters_copy, boardId, False)[:25])
        words_mv = set(words_mv)
        if boardId:
            words_mv = sorted(words_mv, key=lambda x: x[0], reverse = True)
        else:
            words_mv = sorted(words_mv, key=lambda x: x[0], reverse = False)
        return words_mv

    def find_associated_words(self, board, word):
        words_as = []
        if word[2]:
            try:
                for i in range(len(word[0])):
                    if word[1][0] == 0:
                        a = self.find_assoc(board, word[1][0], word[1][1] + i, False, False)
                        if len(a[0]) > 1: words_as.append(a)
                    elif word[1][0] == 14:
                        a = self.find_assoc(board, word[1][0], word[1][1] + i, False, True)
                        if len(a[0]) > 1: words_as.append(a)
                    else:
                        a = self.find_assoc(board, word[1][0], word[1][1] + i, False, True)
                        if len(a[0]) > 1: words_as.append(a)
                        a = self.find_assoc(board, word[1][0], word[1][1] + i, False, False)
                        if len(a[0]) > 1: words_as.append(a)
            except IndexError: pass
        else:
            try:
                for i in range(len(word[0])):
                    if word[1][1] == 0:
                        a = self.find_assoc(board, word[1][1], word[1][0] + i, True, True)
                        if len(a[0]) > 1: words_as.append(a)
                    elif word[1][1] == 14:
                        a = self.find_assoc(board, word[1][1], word[1][0] + i, True, False)
                        if len(a[0]) > 1: words_as.append(a)
                    else:
                        a = self.find_assoc(board, word[1][1], word[1][0] + i, True, True)
                        if len(a[0]) > 1: words_as.append(a)
                        a = self.find_assoc(board, word[1][1], word[1][0] + i, True, False)
                        if len(a[0]) > 1: words_as.append(a)
            except IndexError: pass
        return words_as

    @staticmethod
    def find_assoc(board, k, i, horizontal, dr):
        formed = []
        if horizontal:
            if dr:
                for j in range(15):
                    try:
                        if board[i][k + j] != '_': formed.append(board[i][k + j])
                        else: break
                    except IndexError:
                        break
                pos = (i, k)
            else:
                for j in range(15):
                    if k - j < 0: break
                    try:
                        if board[i][k - j] != '_': formed.append(board[i][k - j])
                        else: break
                    except IndexError:
                        break
                formed.reverse()
                pos = (i, k - len(formed) + 1)
        else:
            if dr:
                for j in range(15):
                    if k - j < 0: break
                    try:
                        if board[k - j][i] != '_': formed.append(board[k - j][i])
                        else: break
                    except IndexError:
                        break
                formed.reverse()
                pos = (k - len(formed) + 1, i)
            else:
                for j in range(15):
                    try:
                        if board[k + j][i] != '_': formed.append(board[k + j][i])
                        else: break
                    except IndexError:
                        break
                pos = (k, i)
        return ''.join(formed), pos, horizontal

    def calculate_points(self, board, n_word, boardId):
        total = 0
        board_copy = deepcopy(board)
        if n_word[2]:
            for i in range(len(n_word[0])):
                board_copy[n_word[1][0]][n_word[1][1] + i] = n_word[0][i]
        else:
            for i in range(len(n_word[0])):
                board_copy[n_word[1][0] + i][n_word[1][1]] = n_word[0][i]
        boardCorrect = self.verifyBoard(board_copy)
        if not boardCorrect:
            return 0, False

        words_eval = [n_word]
        if n_word[3]:
            words_eval.extend(self.find_associated_words(board_copy, n_word))
        for word in words_eval:
            points, overall = 0, 1
            for i in range(len(word[0])):
                tile_points = Board.points[word[0][i]]
                if word[2]:
                    idx = word[1][0] * 15 + word[1][1] + i
                    blank = idx in Board.special_cells[boardId] and board[word[1][0]][word[1][1] + i] == '_'
                else:
                    idx = (word[1][0] + i) * 15 + word[1][1]
                    blank = idx in Board.special_cells[boardId] and board[word[1][0] + i][word[1][1]] == '_'
                if blank:
                    x = Board.special_cells[boardId][idx]
                    if x == "DL":
                        tile_points *= 2
                    elif x == "TL":
                        tile_points *= 3
                    elif x == "DW":
                        overall *= 2
                    elif x == "TW":
                        overall *= 3
                points += tile_points
            total += points * overall
        if n_word[4]: total += 40
        return total, boardCorrect

    def verifyBoard(self, board):
        words_vr = set()
        for row in board:
            words_vr.update(getFullWords(row))

        for k in range(15):
            column = [board[i][k] for i in range(15)]
            words_vr.update(getFullWords(column))

        for word in words_vr:
            if not self.twl06.verifyWord(word):
                return False
        return True

    def loop(self):
        while True:
            self.boards = []
            self.get_games()
            self.getStatus()
            for i_ in range(len(self.boards)):
                board = self.boards[i_]
                if board.move_count == 0:
                    best_moves = self.get_first_moves(board.letters, board.boardId)
                else:
                    best_moves = self.get_best_moves(board.board, board.letters, board.boardId)
                    # if board.endgame: # at attempt at endgame minimax, not as useful since the endgame is too short
                    #     top = []
                    #     for word in best_moves[:25]:
                    #         board_copy = deepcopy(board)
                    #         if word[1][2]:
                    #             for i in range(len(word[1][0])):
                    #                 board_copy.board[word[1][1][0]][word[1][1][1] + i] = word[1][0][i]
                    #         else:
                    #             for i in range(len(word[1][0])):
                    #                 board_copy.board[word[1][1][0] + i][word[1][1][1]] = word[1][0][i]
                    #         try:
                    #             best_opponent_move = self.get_best_moves(board_copy.board, board.letter_count, board.boardId)[0][0]
                    #         except IndexError:
                    #             best_opponent_move = 0
                    #         top.append((word[0] - best_opponent_move, word[1]))
                    #     best_moves = sorted(top, key=lambda x: x[0], reverse = True)
                placed = False
                for i in range(50):
                    try:
                        word = best_moves[i]
                    except IndexError:
                        break
                    move = []
                    for j in range(len(word[1][0])):
                        if word[1][0][j] in board.letters:
                            char = word[1][0][j]
                            x = word[1][1][1] + j if word[1][2] else word[1][1][1]
                            y = word[1][1][0] + j if not word[1][2] else word[1][1][0]
                            if '' in board.letters and board.letters[''] > 0 and Board.points[char] == 1:
                                move.append([x, y, char, True])
                                board.letters[''] -= 1
                            else: move.append([x, y, char, False])
                    result = self.place(board.gameId, move, [word[1][0]])
                    if result['status'] != 'error':
                        result = result['content']
                        points = result['points']
                        print("Played {word} for {points} points, {j} tries".format(word=word[1][0], points=points, j=i + 1))
                        placed = True
                        break
                if not placed:
                    self.swapHelper(board)
            print("Sleeping for a few 😁...")
            sleep(300)

    def swapHelper(self, board):
        toSwap = []
        if '' in board.letters:
            toSwap.extend([''] * board.letters[''])
            board.letters[''] = 0
        rack = list(board.letters)
        r = len(rack)
        if r > 0:
            for _ in range(r):
                char = rack[int(random() * r)]
                if board.letters[char] <= 0: continue
                board.letters[char] -= 1
                toSwap.append(char)
            r = self.swap(board.gameId, toSwap)['content']
            try:
                print("Swapped {r} tiles, {tiles}".format(r=len(r['new_tiles']), tiles=toSwap))
            except KeyError:
                self.passRound(board.gameId)
                print("Passed :(")
        else:
            self.passRound(board.gameId)
            print("Passed :(")

def getPartWords(seq, k, neighbours, horizontal = True):
    words_pt = []
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            word = ''.join(seq[i:j])
            bingo = word.count('_') == 7
            if word.count('_') != 0 and word.count('_') != len(word):
                if horizontal:
                    words_pt.append((word, (k, i), horizontal, False, bingo))
                else:
                    words_pt.append((word, (i, k), horizontal, False, bingo))
            elif word.count('_') == len(word):
                try:
                    if seq[j] != '_' or seq[i-1] != '_': continue
                except IndexError:
                    continue
                if horizontal:
                    for neighbour in neighbours:
                        w = ''.join(neighbour[i:j])
                        if w.count('_') != 0 and w.count('_') != len(w):
                            words_pt.append((word, (k, i), horizontal, True, bingo))
                            break
                else:
                    for neighbour in neighbours:
                        w = ''.join(neighbour[i:j])
                        if w.count('_') != 0 and w.count('_') != len(w):
                            words_pt.append((word, (i, k), horizontal, True, bingo))
                            break
    return words_pt

def getFullWords(seq):
    words_fl = []
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            try:
                if seq[i - 1] != '_' or seq[j + 1] != '_': continue
            except IndexError: pass
            word = ''.join(seq[i:j+1])
            if len(word) > 1 and word.count('_') == 0: words_fl.append(word)
    return words_fl