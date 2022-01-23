import json
import time
import os

#dirname = os.path.dirname(__file__)
#dirname = os.getcwd()
dirname = os.path.dirname(__file__)
file_name = dirname + '/data/input/file_list.json'
#dirname + '/data/input/file_list.json'

#file_type = 'StravaToken'

def jsonLoader(file_type):
    with open(file_name) as f:
        file_list = json.load(f)
        #input_file = file_list[file_type]
        input_file = dirname + file_list[file_type]

    with open(input_file) as f:
        #access_credentials  = json.load(f)
        file_data = json.load(f)

    return(file_data)

def textLoader(file_type):
    with open(file_name) as f:
        file_list = json.load(f)
        input_file = dirname + file_list[file_type]

    with open(input_file) as f:
        file_data = f.read()

    return(file_data)

def jsonWriter(file_type, output):
    with open(file_name) as f:
        file_list = json.load(f)
        output_file = dirname + file_list[file_type]
        print('Writing to... ', output_file)

    with open(output_file, 'w') as outfile:
        json.dump(output, outfile)

def textWriter(file_type, output):
    with open(file_name) as f:
        file_list = json.load(f)
        output_file = dirname + file_list[file_type]

    if file_type == 'shack_post':
        time_str = time.strftime("%Y%m%d-%H%M%S")
        output_file += '_' + time_str + '.txt'

    with open(output_file, 'w') as outfile:
        print('Writing to... ', output_file)
        outfile.write(output)

def main():
    print(f'{os.path.basename(__file__)} has no main code, only functions.')

if __name__ == '__main__':
    main()