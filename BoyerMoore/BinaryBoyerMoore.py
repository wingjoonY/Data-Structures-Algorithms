import sys
"""
FIT3155 Assignment 1 Question 2
Optimizing Boyer-Moore for binary strings

Student Name: Yap Wing Joon
Student ID: 31862527
"""
    
    
def z_algorithm(string):
    
    n = len(string)
    
    z = [0] * n
    z[0] = n
    
    l, r = 0, 0

    for i in range(1, n):
        
  
        if i <= r:
            
            k = i - l

            if z[k] < r - i + 1:
                
                z[i] = z[k]
            
    
            elif z[k] > r - i + 1:
                
                z[i] = r - i + 1
            
            elif z[k] == r - i + 1:
                
                l = i
                while r + 1 < n and string[r - l + 1] == string[r + 1]:
                    
                    r +=  1
                    
                z[i] = r - l + 1
        
        else:
            
            l, r = i,i
            
            while r < n and string[r] == string[r-l]:
                
                r += 1
                
            z[i] = r - l
            r -= 1
            
    return z

# going to keep the extended bad character rule implementation here but commented because its part of the original boyer moore
# def compute_extended_bad_char(pattern):
#     # just following lecture slides
#     # using Rk(x) table
#     m = len(pattern)
#     bad_char_table = [[0] * 2 for _ in range(m)]  
    
#     for j in range(m - 1):
#         for i in range(2):  
#             bad_char_table[j + 1][i] = bad_char_table[j][i]
        
       
#         char_index = ord(pattern[j]) - ord('0')  
#         bad_char_table[j + 1][char_index] = j + 1

#     return bad_char_table
    
    
def compute_good_suffix(pattern):
    # also just following the lecture slides
    m = len(pattern)
    reversed_pat = pattern[::-1]
    
    z_suffix = z_algorithm(reversed_pat)
    z_suffix.reverse()
    
    good_suffix = [0] * (m + 1)  
    
    for p in range(m - 1):
       
        j = m - z_suffix[p]
        good_suffix[j] = p + 1
    

    return good_suffix


def compute_matched_prefix(pattern):
    
    m = len(pattern)
    
    z_values = z_algorithm(pattern)
    
    z_values.append(0)
    # traversing from the back
    for i in range(m - 1, -1, -1):

        # using previous z val 
        if z_values[i] + i < m:
            
            z_values[i] = z_values[i + 1]


    return z_values

def boyer_moore(text, pattern):
    
    m = len(pattern) - 1
    n = len(text)
    
    # preprocessing boyer-moore things
    # bad_char_table = compute_extended_bad_char(pattern)
    good_suffix_table = compute_good_suffix(pattern)
    matched_prefix_table = compute_matched_prefix(pattern)
    comparison_counter = 0
    
    matches = []
    j = 0 # current pos of pattern in text

    start, stop = 0, m # failed attempt at galil's optim
    
    
    while j <= n - m:
        
        k = m # current position for right-to-left scanning

        # galil is optimising my death broooooooo wth ;-;
        while k >= 0 and pattern[k] == text[j + k - 1] and j + k - 1 >= 0: 
            # j + k - 1 >= 0 cause it would go to text[-1] 
            
            comparison_counter += 1
            
            k -= 1
            
        # pattern match
        if k < 0:
                        
            matches.append(j + k + 1)
            
            start = j + m - matched_prefix_table[1]
            stop = j + m - matched_prefix_table[1] + matched_prefix_table[1] - 1
            
            # shift by matchedprefix(2) (1 here cause my mp arr is 0 based index)
            j += max(1, m - matched_prefix_table[1])

        
        else:
            
            
            # x = text[j + k - 1]
            

            # bad_char_shift = max(1, k - bad_char_table[k][ord(x) - ord('0')]) # k - R(x) 
            
            good_suffix_shift = 0 
            
            if good_suffix_table[k + 1] > 0:
                
                good_suffix_shift = m - good_suffix_table[k + 1] 
                stop = good_suffix_table[k + 1]
                start = good_suffix_table[k + 1] - m + k + 1
                
            else:
                
                good_suffix_shift = m - matched_prefix_table[k + 1]
                stop = matched_prefix_table[k + 1]
                start = 0

            
            # just use 1 instead of computing bad character rule lol
            j += max(1, good_suffix_shift)
    
    return matches, comparison_counter

        
def read_file(filename):

    file_string = ""
    with open(filename, 'r') as file:
        for line in file:
            file_string += line.strip()  
            
    return file_string


if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        sys.exit(1)
    
    
    filename1 = sys.argv[1]
    filename2 = sys.argv[2]
    
    text_content = read_file(filename1)
    pattern_content = read_file(filename2)

    
    output = boyer_moore(text_content, pattern_content)
    matches = output[0]
    comparisons = output[1]
    print("Number of comparisons:", comparisons)
    
    with open("output_a1q2.txt", "w") as output_file:

        for position_of_match_in_txt in matches:
            
            output_file.write(f"{position_of_match_in_txt}\n")



