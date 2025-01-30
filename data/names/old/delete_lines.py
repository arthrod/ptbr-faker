def delete_lines():
    input_file = '/Users/arthrod/Library/CloudStorage/GoogleDrive-arthursrodrigues@gmail.com/My Drive/acode/atemp-drive/ptbr-faker/data/population_data_2024_with_postalcodes_updated.json'
    output_file = input_file + '.tmp'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep lines before 2227774 and after 2936823
    new_lines = lines[:2227774] + lines[2936823:]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # Replace original file with new file
    import os
    os.replace(output_file, input_file)
    print("Lines deleted successfully")

if __name__ == '__main__':
    delete_lines()
