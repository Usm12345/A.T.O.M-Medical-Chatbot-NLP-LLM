# A.T.O.M Chat-bot 

# Introduction
A.T.O.M is a chatbot developed using Django, AIML (Artificial Intelligence Markup Language),
Pytholog (Prolog in Python), OpenAI API, and Neo4j. The chatbot provides conversational
interaction with users, answering questions, and assisting with various tasks.


**Features**
1. User Authentication: A.T.O.M requires users to authenticate themselves before accessing the
chatbot interface. Only authenticated users can interact with the chatbot.
2. AIML Integration: AIML is used to provide predefined responses to specific patterns of user
messages. The chatbot is trained on AIML files to understand and respond to user queries.
3. OpenAI Integration: OpenAI API is used to generate creative responses for user queries. It
enhances the chatbot's ability to provide relevant and engaging answers.
4. Prolog Integration: Pytholog, which is Prolog implemented in Python, is used for logic
programming. Prolog rules can be applied to user queries to derive additional information or
generate responses.
5. Neo4j Integration: Neo4j is used as a graph database. User information is stored as nodes in
Neo4j, and a relationship is created between the user node and the A.T.O.M node in the graph.
6. User Interaction: Users can send messages to the chatbot through the web interface. The
chatbot processes the messages and generates appropriate responses based on the
implemented logic.


**Prerequisites**
1. Django: The project is built using the Django web framework. Ensure that Django is installed.
2. AIML: The AIML library is used for natural language processing. Install AIML using pip install
python-aiml.
3. Pytholog: Pytholog is used for logic programming. Install Pytholog using pip install
pytholog.
4. OpenAI API: A valid OpenAI API key is required to interact with the OpenAI language model.
Sign up for OpenAI and obtain an API key.
5. Neo4j: Neo4j is used as the graph database. Install Neo4j and set up the necessary
configurations.


**Installation and Setup**
1. Clone the project repository from GitHub.
2. Install the required dependencies mentioned in the Prerequisites section.
3. Update the openai_api_key variable in the code with your valid OpenAI API key.
4. Configure the Neo4j connection in the graph variable by providing the appropriate URL,
username, and password.
5. Run database migrations using <code>python manage.py migrate</code>.
6. Start the Django development server using <code>python manage.py runserver</code>.

**Usage**
1. Access the chatbot web interface by navigating to the provided URL in a web browser. 
2. If you are not already authenticated, click on the "Login" link and enter your credentials or click
on the "Register" link to create a new account.
3. Once authenticated, you can interact with the chatbot by entering messages in the input field
and pressing Enter or clicking the "Send" button.
4. The chatbot will process your message and provide a response based on the implemented logic.
5. Conversations with the chatbot are stored and displayed on the web interface.
6. User information is stored as nodes in Neo4j, with a relationship created between the user node
and the A.T.O.M node.
7. You can log out from the chatbot by clicking on the "Logout" link.

**Project Structure**
The project contains the following files:
1. models.py: Defines the database models, including the Chat model for storing user
interactions.
2. views.py: Contains the view functions for handling user requests and rendering templates.
3. main.html: HTML template for the chatbot interface.
4. login.html: HTML template for the login page.
5. register.html: HTML template for the registration page.


**Conclusion**
A.T.O.M is a chatbot built using Django, AIML, Pytholog, OpenAI API, and Neo4j. It provides
conversational interaction with users and incorporates AI-powered response generation. By
following the installation and usage instructions, users can interact with the chatbot and receive
personalized responses.
