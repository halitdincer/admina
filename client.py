from server import Message, send_message

def main():

    while True:
        prompt = input("You > ").strip()

        # Break the loop for 'exit' prompt
        if prompt == 'exit':
            break

        # Send the message and print out the response
        print("Atlas > ", send_message(Message("user", prompt)))

if __name__ == "__main__":
    main()
