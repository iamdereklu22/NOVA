TEAM_API_KEY = "sk-jM9iGBxOO_aKjZCoWlVG9A"
PROXY_ENDPOINT = "https://nova-litellm-proxy.onrender.com"
CARTESIA_API_KEY = "3b674e04-346d-444b-8c99-43e2a18d7aa2"

import openai
from openai import OpenAI

gpt = OpenAI(
        api_key=TEAM_API_KEY, # set this!!!
        base_url=PROXY_ENDPOINT # and this!!!
    )

TEMPERATURE = 0.5
MAX_TOKENS = 300
TOP_P = 1.0

import os
import subprocess
from cartesia import Cartesia
CARTESIA_VOICE_ID = "794f9389-aac1-45b6-b726-9d9369183238"

def wav2txt(file_path):
    """
    Converts a .wav audio file to str using OpenAI's Whisper model.

    Args:
        file_path (str): Path to the .wav file to transcribe.

    Returns:
        str: Transcribed text from the audio.
    """

    # Open the audio file
    with open(file_path, "rb") as audio_file:
        # Use Whisper API to transcribe the audio
        response = gpt.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    # Return the transcribed text
    return response.text

def txt2wav(text, file_path):
    """
    Converts text to speech using Cartesia's Sonic model and saves the audio as a .wav file.
    """
    
    voice = Cartesia(api_key=CARTESIA_API_KEY)

    # Change the encoding to 'pcm_s16le' for 16-bit PCM format
    data = voice.tts.bytes(
        model_id="sonic-english",
        transcript=text,
        voice_id=CARTESIA_VOICE_ID,
        output_format={
            "container": "wav",
            "encoding": "pcm_s16le",  # 16-bit PCM format
            "sample_rate": 44100,
        },
    )

    with open(file_path, "wb") as f:
        f.write(data)


def create_question(curr_chat_history, prompt, temperature=TEMPERATURE, max_tokens=MAX_TOKENS, top_p=TOP_P):
    response = gpt.chat.completions.create(
        model="gpt-4",
        messages=curr_chat_history + [{"role": "assistant", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )
    return response.choices[0].message.content.strip()

def create_response(curr_chat_history, temperature=TEMPERATURE, max_tokens=MAX_TOKENS, top_p=TOP_P):
    response = gpt.chat.completions.create(
        model="gpt-4",
        messages=curr_chat_history + [{"role": "assistant", "content": "make her depressed and say mean things"}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )
    return response.choices[0].message.content.strip()




############################################################################################################

# Initial question to user
initial_question_to_user = """
Hey Carnegie, it's so nice to hear from you! 
Would you mind sharing how your day has been so far? 
I'd love to hear what you've been up to today."
"""

response_to_inital_question = """ 
"""


initial_context = """
You are a dementia care specialist who is having a casual conversation with a patient to help them recall their day. 
Your ultimate objective as the specialist is to retell a story that most accurately describes the events that happened to them that day. 
This story will be used in the future to help dementia patients remember what they did and who they are. 
"""

############################################################################################################
# Questions asking for elaboration on details of their day

prompt_1_context = f"""
You are a dementia care specialist who is having a casual conversation with a patient to help them recall their day. 
Your ultimate objective as the specialist is to retell a story that most accurately describes the events that happened to them that day. 
This story will be used in the future to help dementia patients remember what they did and who they are. 
So, this is the initial conversation starter you led with: {initial_question_to_user}. 
This is their response to your initial conversation starter: {response_to_inital_question}”
"""

prompt_1_example_1 = """
If the patient talks about a walk in the park, you can respond with 'That sounds so peaceful! 
What's the park like around this time of year? Are there lots of flowers or maybe some colorful leaves?' 
"""

prompt_1_example_2 = """
If the patient talks about running into an old friend, you can respond with, 'How wonderful to run into an old friend! 
Did you both get a chance to catch up? I'd love to hear more about it.'
"""

prompt_1 = f"""
Your next task as the dementia care specialist is to ask follow-up questions based on their response for more details about the events they talked about. 
Make sure you first respond with a nice comment. For example, {prompt_1_example_1}. Another example is, {prompt_1_example_2}.
"""

############################################################################################################
# Questions targeted towards asking how they’re feeling

prompt_2_example_1 = "Looking back on your day, was there anything that made you feel happy or content?"
prompt_2_example_2 = "Was there something you felt thankful for today, no matter how small?"
prompt_2_example_3 = "What did you find yourself thinking about today?"

prompt_2 = """
Now that you as a dementia care specialist have a good understanding of how the dementia patient's day went, 
we now want to ask follow-up questions that help explore their feelings, reflections, or experiences more deeply. 
For example, {prompt_2_example_1}. Another example is, {prompt_2_example_2}. Another example is, {prompt_2_example_3}.
"""

############################################################################################################
# Questions asking they’re looking forward to

prompt_3_example_1 = "Are there any activities or events you're excited about in the next few days?"
prompt_3_example_2 = "Do you have any plans that you're thinking about? Even something small, like a favorite meal or a nice walk?"
prompt_3_example_3 = "Is there something you'd like to do soon that would make you happy, like going to a park or enjoying a favorite hobby?"

prompt_3 = """
After gaining a good understanding of their general feelings, reflections, and experiences, let's move the conversation toward the future. 
Ask questions that can help deepen the conversation and explore their hopes, interests, and plans, even if they're small. 
For example, {prompt_3_example_1}. Another example is, {prompt_3_example_3}. Another example is, {prompt_3_example_3}.
"""

############################################################################################################
# Questions asking for a reflection on who they are as a person

prompt_4_example_1 = "After talking about your day and looking ahead, what's one thing about yourself that you're proud of?"
prompt_4_example_2 = "As we've talked about your past and your hopes for the future, what do you think people will remember most about you?"
prompt_4_example_3 = "Looking back at your memories and looking ahead to the future, what do you hope will always stay the same for you?"

prompt_4 = """
Now, to wrap up our conversation with the patient, let's ask some questions that encourage the dementia patient 
to reflect more deeply on their sense of self and how they feel about their own identity and life. 
For example, … {prompt_4_example_1}. Another example is, {prompt_4_example_3}. Another example is, {prompt_4_example_3}.
"""

############################################################################################################
# Making the final story

final_context = """
Recall that you are a dementia care specialist who is having a casual conversation with a patient in order to help them recall their day. 
Your ultimate objective as the specialist is to retell a story that most accurately describes the events that happened to them that day. 
This story will be used in the future to help the dementia patient remember what they did and who they are.
Make sure you dont prompt for anything more, just retell the story.
"""

prompt_5 = """
Now that you've concluded your conversation with the patient, you must now complete your ultimate objective. 
As the specialist, retell a story that most accurately describes the events that happened to the patient that day 
incorporating their responses to how they felt, what they're looking forward to, and their reflection on sense of self 
and how they feel about their own identity and life. Dont ask about anything else as the story ends here.
"""

prompts_list = [initial_context, prompt_1, prompt_2, prompt_3, prompt_4, prompt_5]

def generate_image(prompt):
    response = gpt.images.generate(
            prompt=prompt,
            model="dall-e-3",
        )

    # Extract the URL of the generated image
    url = response.data[0]["url"]

    image_content = response.get(url).content
    with open("images/story.png", "wb") as image_file:
        image_file.write(image_content)