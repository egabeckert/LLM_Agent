from generate_content import generate_content

def main():
    messages = [
        {"role": "user", "content": "What is 10 plus 5?"}
    ]
    response = generate_content(messages, verbose=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    main()
