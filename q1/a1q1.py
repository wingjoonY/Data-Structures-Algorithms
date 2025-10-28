import sys
"""
FIT3155 Assignment 1 Question 1
Near-exact pattern matching under DL-distance ≤ 1

Student Name: Yap Wing Joon
Student ID: 31862527
    
"""
def z_algorithm(string):
    
    n = len(string)
    
    # initialize the z array with all 0s and set z[0] to the length of the whole string (prefix at 0 is the whole string)
    z = [0] * n
    z[0] = n
    
    
    l, r = 0, 0

    # starting from 2nd char in the text
    for i in range(1, n):
        
        # if curr within the z-box
        if i <= r:
            
            # set k to the previously computated Z-value in the mirrored position
            k = i - l
            
            # if the previously computed Z-value is less than the length of the remaining string in the current Z-box
            if z[k] < r - i + 1:
                
                # then we can copy the Z-value from pos k because it matches the remaining portion in the Z-box
                z[i] = z[k]
            
            # else if the previously computed Z-value at k extends longer than the remaining string in the current Z-box
            elif z[k] > r - i + 1:
                
                # we can conclude that the current Z-box is the remaining length
                z[i] = r - i + 1
            
            # if the previously computed Z-value at pos k exactly matches the remaining length of the Z-box
            elif z[k] == r - i + 1:
                
                l = i

                # have to do comparison from r + 1 onwards
                while r + 1 < n and string[r - l + 1] == string[r + 1]:
                    
                    r +=  1
                    
                z[i] = r - l + 1
        
        
        else:
            
            # new z-box
            l, r = i,i
            
            # continue comparing characters until mismatch occurs
            while r < n and string[r] == string[r-l]:
                
                # make z box longer :)
                r += 1
            
            
            z[i] = r - l
            r -= 1
            
    return z


def reverse_string(string):

    return string[::-1]  

   
def near_exact_pattern_matching(text, pattern):

    m = len(pattern)
    
    z_string = pattern + '$' + text 
    
    reversed_pat = reverse_string(pattern)
    reversed_text = reverse_string(text)
    
    reversed_z_string = reversed_pat + '$' + reversed_text 
    
    z_values = z_algorithm(z_string)
    reversed_z_values  = z_algorithm(reversed_z_string)

    dldist_one = []


    for i in range(m + 1, len(z_values)):
 
        reverse_i = len(z_values) + m - i # to start from the back of the reverse z arr
       
        # Will use examples (T = "abcd") for justification
        
        # when T matches S by default
        if z_values[i] == m:
            
            dldist_one.append((i + 1 - (m + 1), 0))
            
        
        # Substitute at the start of S
        # Example: xbcd -> abcd
        # we check the reversed z values to find dcb or z[i] = 3
        elif reversed_z_values[reverse_i - m + 1] == m - 1:
            
            dldist_one.append((i + 1 - (m + 1), 1))

        # Substitute in between S
        # Example: axcd -> abcd
        # check normal z values to find a or z[i] = 1 and then reverse array to find dc or z[i] = 2  
        elif z_values[i] + reversed_z_values[reverse_i - m + 1] == m - 1:
            
            dldist_one.append((i + 1 - (m + 1), 1))

        # Substitute at the end of S 
        # Example: abcx -> abcd
        # same as start case but use normal z values array
        elif z_values[i] == m - 1:
            
            dldist_one.append((i + 1 - (m + 1), 1))
        
        # Insert at the start of S
        # Example (includes redundant case): xbcd -> abcd
        elif reversed_z_values[reverse_i - m + 2] == m - 1 or reversed_z_values[reverse_i - m + 2] == m:
            
            dldist_one.append((i + 1 - (m + 1), 1))
        
        # Insert in the middle of S
        # Example: acdx -> abcd 
        elif z_values[i] + reversed_z_values[reverse_i - m + 2] == m - 1:
            
            dldist_one.append((i + 1 - (m + 1), 1))
        
        # Insert at the end of S
        # Example: abcx -> abcd
        elif z_values[i] == m - 1:
            
            dldist_one.append((i + 1 - (m + 1), 1))
        
        # Delete somewhere in S
        # Example1: abxcd -> abcd 
        # Example2: (redundant case): yabcd -> abcd
        elif z_values[i] + reversed_z_values[reverse_i - m] == m:
            
            dldist_one.append((i + 1 - (m + 1), 1))
                
        # Transposition/ Swap
        # The slicing should be O(1) time since the slicing values are constant (2 chars)
        elif z_values[i] + reversed_z_values[reverse_i - m + 1] == m - 2:
            
            # Swap at the first 2 chars of S 
            # Example: bacd -> abcd 
            # just need to compare first 2 character (and swap them) at i and the first 2 character of pat
            if z_values[i] == 0 and text[i - (m + 1) + 1] + text[i - (m + 1)] == pattern[0:2]: 
                
                dldist_one.append((i + 1 - (m + 1), 1)) 
            
            # Swap at the last 2 chars of S 
            # Example: abdc -> abcd 
            # just need to compare last 2 character at the position and the last 2 character of pat (m-2 to m)
            # use i + z_val[i] to find the mismatch character and then use that pos + 1 to get the next char, swap and compare 
            elif reversed_z_values[reverse_i - m + 1] == 0 and text[i - (m + 1) + 1 + z_values[i]] +  text[i - (m + 1) + z_values[i]] == pattern[m - 2: m]: 
                
                dldist_one.append((i + 1 - (m + 1), 1))
            
            # Swap at the middle of S 
            # Example: acbd -> abcd 
            # same idea as previous case (last 2 char of S) but the 2 char from pat have to be 
            # derived from z_value to z_value + 2 since we don't know where in the middle exactly
            elif z_values[i] != 0 and reversed_z_values[reverse_i - m + 1] != 0 and text[i - (m + 1) + 1 + z_values[i]] + text[i - (m + 1) + z_values[i]] == pattern[z_values[i]:z_values[i] + 2]:
                
                dldist_one.append((i + 1 - (m + 1), 1)) 
        
                
    return dldist_one


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

    
    output = near_exact_pattern_matching(text_content, pattern_content)
    
    with open("output_a1q1.txt", "w") as output_file:

        for position_in_txt, DL_distance_with_pat in output:
            output_file.write(f"{position_in_txt} {DL_distance_with_pat}\n")
