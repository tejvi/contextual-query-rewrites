import os
import shutil

def split(delimiter_list, input_file, output_path, chunk_size = 0, replace_with='\n'):
    
    file = open(input_file, 'r')

    if not chunk_size:
        output_file = open(output_path, 'wb')
        for line in file.readlines():
            
            for delimiter in delimiter_list:
                line = line.replace(delimiter, replace_with)
            output_file.write(line.encode())
        file.close()
        output_file.close()
        
    
    
    else:
        contents = file.readlines()
        file.close()

        if os.path.isdir(output_path):
            shutil.rmtree(output_path)
        
        os.mkdir(output_path)             

        for i in range(0, len(contents), chunk_size):
            outfile = open(os.path.join(output_path, "data_{0}.txt".format(i)), 'wb')

            for line in contents[i : i + chunk_size]:
                
                for delimiter in delimiter_list:
                    line = line.replace(delimiter, replace_with)
                outfile.write(line.encode())
            
            outfile.close()


def merge_wikifuse(input_path, output_file):
    outfile = open(output_file, 'wb')

    if os.path.isfile(input_path):
        file = open(input_path, 'r').readlines()
        
        for i in range(0, len(file), 3):
            line = " {0} \t {1} <::::> {2} \n".format(file[i].strip(), file[i + 1].strip(), file[i + 2].strip())
            outfile.write(line.encode())
    else:
        for inp_file in os.listdir(input_path):
            file = open(os.path.join(input_path, inp_file), 'r').readlines()
            for i in range(0, len(file), 3):
                line = " {0} \t {1} <::::> {2} \n".format(file[i].strip(), file[i + 1].strip(), file[i + 2].strip())
                outfile.write(line.encode())
    
    outfile.close()



            

