"""
_______________________________________________________________________________________________________________________________________________


QUESTION 2: catGPT

_______________________________________________________________________________________________________________________________________________
"""

class Node:
    def __init__(self,data = "", level = None):
        
        """
        Function description:

            Constructor for the Node class
            link - a list the links between this node and other nodes where the index corresponds to the position at which the letter is located
                    in the alphabet (a = 1, b = 2,...), the extra slot is for the terminal / ending marker node node
            highest_frequency_node - the node that appears most frequently coming from this node
            data - alphabetical letters that represent the node 
            level - the level/ length at which the node is
            frequency - the number of times this node appears in the given sentence
            
        Input:
        
            data - alphabetical letters that represent the node (default is an empty string)
            level - the level/ length at which the node is
            
        Time complexity: O(1)
        """
        
        self.link = [None] * 27 
        self.highest_frequency_node = self
        self.data = data
        self.level = level
        self.frequency = 0
        
        
class CatsTrie:
    
    def __init__(self, sentences):
        
        """
        Function description:

            Constructor for the CatsTrie class
            root - the node which all sentences start from
        
        Approach description:
        
            All sentences will be inserted into CatsTrie when initialized since we need to insert all sentences and therefore need to iterate through
            sentences we will require at least O(N) where N is the number of sentences. The "insert" function takes O(M) time where M is the number
            of characters in the longest sentence/ number of characters in each sentence. 
            
            
        Input:
        
            sentences - the list of given sentences
            
        Time complexity: O(NM)
        """
        
        self.root = Node(level=0)
        for sentence in sentences: 
            
            self.insert(sentence)    
            
            
    def insert(self, sentence):
        
        """
        Function description:

            Uses "insert_aux" to add the sentence starting from the root
            
            
        Input:
        
            sentence - a sentence from the list of sentences
            
        Time complexity: O(M) where M is the length of the longest sentence
        """
        
        current = self.root
        self.insert_aux(current,sentence)
        
    def insert_aux(self, current_node, sentence):
        
        """
        Function description:

            Recursively inserts each sentence into CatsTrie and finds the "highest_frequency_node" of each node
            
        Approach description:
        
            Firstly we neded to check if we have reached the end of the sentence. We do that by comparing "count_level" and the length of the 
            sentence to check if the sentence is done inserting; a terminal node is added just to check if that position/ link[0] is None or not.
            Then using the ASCII value for each letter we can find get the index corresponding to its position in the alphabet. We do a check if that
            position for the current node is empty to see if it already exists. If it does not, then we add a new node with the current prefix of
            the sentence corresponding to the "count_level". If it does exist, it will recursively call itself to move on to the next letter in
            the sentence. Everytime we reach the end of a sentence, we increment its frequency by one and do a check if that node is the most
            frequently appearing one and if it is lexicographically smaller if frequency is the same. We will then return the current node being
            used and do the check for frequency and lexicographic order and update "highest_frequency_node" coming from the current node. 
            Note that the first check is to ensure that the last non terminal node also updates its "highest_frequency_node" if there it is not itself.
            
            
        Input:

            current_node - the node the current function call is using
            sentence - a sentence from the list of sentences
            
        Time complexity: O(M)
        """
        
        current = current_node
        count_level = current.level
        new_node = None
        
        if count_level == len(sentence):
            if current.link[0] is None:
                terminal = Node(data="$", level = count_level + 1)
                current.link[0] = terminal
                
                # updates non terminal ending node's frequency
                current.frequency += 1
                
            else:
                
                current.frequency += 1
            
            # checks if there are more frequently appearing sentences along this sentence
            if current.frequency > current.highest_frequency_node.frequency:
                current.highest_frequency_node = new_node
            
            elif current.frequency == current.highest_frequency_node.frequency:
                if current.data < current.highest_frequency_node.data:
                    current.highest_frequency_node = current

            return current
        
        # index mapping using ASCII values
        index = ord(sentence[count_level]) - 97 + 1
        if current.link[index] is None:
            
            # creates new node 
            next_char = Node(data = current.data + sentence[count_level],level = count_level + 1)
            current.link[index] = next_char
            
            # recursive call to move on the next character
            result = self.insert_aux(next_char,sentence)
            new_node = result
            
        else:
            
            # recursive call when the node already exists
            result = self.insert_aux(current.link[index],sentence)
            new_node = result
            
        # second check for all previous nodes
        if new_node.frequency > current.highest_frequency_node.frequency:
            current.highest_frequency_node = new_node
           
        elif new_node.frequency == current.highest_frequency_node.frequency:
            if new_node.data < current.highest_frequency_node.data:
                current.highest_frequency_node = new_node
        
        return current.highest_frequency_node
    
    def search(self, sentence):
        
        """
        Function description:

            Uses "seach_aux" to find if the sentence given exists
            
        Input:

            sentence - a sentence from the list of sentences
            
        Output:
        
            the sentence if it exists and None if not
            
        Time complexity: O(M)
        """
        
        result = None
        current = self.root
            
        search_result = self.search_aux(current , sentence)
        
        if search_result is not None:
            
            result = search_result
        
        return result
    
    
    def search_aux(self, current_node, sentence):
        
        """
        Function description:

            Recursively searches for the given sentence 
           
        Input:

            current_node - the node the current function call is using
            sentence - a sentence from the list of sentences
            
        Time complexity: O(M)
        """
        
        current = current_node
        count_level = current.level
    
        if count_level == len(sentence):
            if current.link[0] is not None:
                
                return current.data
            
            else:
            
                return None
        
        index = ord(sentence[count_level]) - 97 + 1
        if current.link[index] is None:
            return None
        
        else:
            
            search_result = self.search_aux(current.link[index],sentence)
        
        return search_result
    
    
    def autoComplete(self, prompt):
        
        """
        Function description:

            Finds a suitable completion of a given prompt
            
        Approach description:
        
            Since the "highest_frequency_node" for all nodes is already set when we insert, all we need to do is find the node where the prompt ends.
            If there is None then return None. If there is then do a search of the "highest_frequency_node"'s data to get the sentence.
            
        Input:

            prompt - a prompt 
            
        Time complexity: O(X + Y)
        """
        
        current = self.root
        promptEndingNode = self.searchPrompt(current, prompt)
        if promptEndingNode is not None:
            
            return self.search(promptEndingNode.highest_frequency_node.data)
            
        return None
    

    def searchPrompt(self, current_node, prompt):
        """
        Function description:

            Finds the ending node of the prompt
            
        Input:

            current_node - yes
            prompt - a prompt 
            
        Time complexity: O(X)
        """
        current = current_node
        count_level = current.level
        
        if count_level == len(prompt):
            return current
        
        index = ord(prompt[count_level]) - 97 + 1
        
        if current.link[index] is not None:
            
            return self.searchPrompt(current.link[index], prompt)
        
        else:
            
            return None


# ------------------ MAIN ---------------------

if __name__ == "__main__":
    
    sentences = ['you', 'i', 'you', 'you', 'me', 'your', 'your', 'you', 'im', 'im', 'i', 'meet', 'meet', 'yoyo']

    mycattrie = CatsTrie(sentences)
    prompt = "yo"
    autoComplete = mycattrie.autoComplete(prompt)
    print(autoComplete)
        
        