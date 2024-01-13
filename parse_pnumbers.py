import os
import re
import json

class OutManager:
    def __init__(self):
        self.output = list()
        self.active_lists = [ list() ]
        self.had_fin_char = False

    def add_char(self, c):
        self.had_fin_char = False
        for l in self.active_lists:
            l.append(c)

    def fin_char(self):
        if self.had_fin_char:
            return 
        self.had_fin_char = True

        has_zero_list = False
        for l in self.active_lists:
            if len(l) > 0:
                self.output.append(l.copy())
            else:
                has_zero_list = True
        
        if not has_zero_list:
            self.active_lists.append(list())
        self.active_lists = [ x for x in self.active_lists if len(x) <= 11 ]

## We basically need a minature lexer to resolve issues here
## On every digt we start a run and grow all runs until they are longer than 11 characters
## On every non-digit we save runs
## eg: mini_lexer("0123 4567 8901 2345")
## ['0123', '01234567', '4567', '012345678901', '45678901', '8901', '456789012345', '89012345', '2345']

def mini_lexer(input_string):
    input = list(input_string)
    
    lst = OutManager()
    for c in input:
        if c.isdigit():
            lst.add_char(c)
        else:
            lst.fin_char()
    lst.fin_char()

    total_out = lst.output
    
    for i, v in enumerate(total_out):
        total_out[i] = ''.join(v)

    total_out = [ x for x in total_out if len(x) >= 8 and len(x) <= 11 ]
    return total_out
    
def filter_int_prefix(string):
    if string[:3] == '356' and len(string) == 11:
        string = string[3:]
    return string

def filter_for_len_and_prefix(string):
    if string[0] != '7' and string[0] != '9':
        return False
    return len(string) == 8
    
def parse(input_string):
    out = set()
    for match in re.findall(r"[^a-zA-Z]{8,}", input_string):
        match = mini_lexer(match)
        match = [ filter_int_prefix(x) for x in match ]
        match = [ x for x in match if filter_for_len_and_prefix(x) ]
        out.update(match)
    return [ '+356' + x for x in out ]

def parse_post(post):
    results = []

    if post["text"]:
        results.extend(parse(post["text"]))

    for comment in post["comments"]:
        if comment[0]:
            results.extend(parse(comment[0]))

        for reply in comment[1]:
            if reply[0]:
                results.extend(parse(reply[0]))

            for subreply in reply[1]:
                if subreply:
                    results.extend(parse(subreply))

    return results

def read_files_in_directory(directory_path):
    file_names = [file_name for file_name in os.listdir(directory_path)]
    out = list()
    for fname in file_names:
        fname = os.path.join(directory_path, fname)
        if not os.path.isfile(fname) or os.path.getsize(fname) == 0:
            continue
        with open(fname, "r", encoding="utf-8") as f:
            out.append(json.load(f))
    return out

def main():
    with open("config.json", "r", encoding="ascii") as f:
        DUMP_DIRECTORY = json.load(f)["DUMP_DIRECTORY"]

    posts = read_files_in_directory(DUMP_DIRECTORY)

    results = []
    for post in posts:
        results.extend(parse_post(post))

    results = list(set(results))
    results.sort()

    for result in results:
        print(result)


if __name__ == "__main__":
    main()
