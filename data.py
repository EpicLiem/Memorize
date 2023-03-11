# read data for player to memorize and write data for player to review
import csv
import random


class Question:
    def __init__(self, question : str, answers : [str], fails: int = 0):
        self.question: str = question
        self.answer: [str] = answers
        self.fails: int = fails

        # minor preprocessing
        for i in range(len(self.answer)):
            self.answer[i]: str = self.answer[i].strip().lower()

    def __str__(self):
        return f"Prompt: {self.question}, Answer: {self.answer}, Fails: {self.fails}"

    def __repr__(self):
        return f"Prompt: {self.question}, Answer: {self.answer}, Fails: {self.fails}"

    def __eq__(self, other):
        return self.question == other.question and self.answer == other.answer and self.fails == other.fails

    def __ne__(self, other):
        return self.question != other.question or self.answer != other.answer or self.fails != other.fails

class Database:
    def __init__(self):
        self.data: [Question] = []

    def read_csv(self, file_name):
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                answers = row[1].split(';')
                try:
                    self.data.append(Question(row[0], answers))
                except:
                    print("Error reading row: " + str(row))

    def write_csv(self, file_name):
        with open(file_name, 'w') as file:
            writer = csv.writer(file)
            for row in self.data:
                writer.writerow([row.question, ';'.join(row.answer), row.fails])

    def add_problem(self, problem):
        self.data.append(problem)

    def remove_problem(self, index):
        self.data.pop(index)

    def get_random_problem(self):
        """
        Returns a random question from the database or None if the there is no data
        """
        try:
            return random.choice(self.data)
        except:
            return None

    def get_problem(self, index):
        """
        Returns the question at the given index or None if the index is out of range
        """
        try:
            return self.data[index]
        except:
            return None


    def __str__(self):
        return f"{self.data}"

    def __repr__(self):
        return f"{self.data}"

    def __eq__(self, other):
        return self.data == other.data