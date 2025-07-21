Of course. Here is the complete and organized transcript of the audio, translated into English and formatted as Markdown.

Part 1: About, Goals, and Professional Story
Question 1: The Elevator Pitch

The Question: If you were to meet a senior manager from Google, Video, or OpenAI in an elevator and had 30 seconds to introduce yourself, what would you say? Who are you, what do you do, and what is your unique quality?

Answer:

My name is Yoni Reich. I am a sworn technology enthusiast, a technologist to an almost exaggerated degree.

What does that mean? It means I am deeply interested in and love new technologies. I enjoy hearing about them, understanding them, figuring out how they work, and ultimately, thinking about how they can be used, how I can use them, how to build things with my own hands, and develop them further.

I started learning at a younger age, teaching myself to code because I wanted to build games and applications. I went on YouTube, started watching videos, and began learning to understand, to develop, and to get to know new things. I didn't set any limits for myself; whatever I wanted to know, I started learning and improving myself. I even had to improve my English to start watching the right videos, because I realized I needed to watch content in English. So I sat by myself, focused, and improved my English so I could later learn development and how to develop software.

I believe my central unique quality lies in the intersection of two things:

The motivation I get from my genuine love for technologies and cool, innovative things.

The ability to sit down by myself, the autodidactic skill, to truly learn the things I need and the tools required to experiment with the concepts I'm passionate about.

For context, this self-driven learning continued professionally. I pursued my bachelor's degree in Computer Science at the Open University. I came to it with no formal background—not even high school matriculation certificates. I had no prior knowledge of mathematics and truly started from scratch at the university. I finished with a degree.

I think this ultimately defines me: this strong drift and motivation that comes from a desire to learn, understand, get to know, experiment, and develop things further. I'm drawn to a wide range of technologies, especially innovative things that are on the cutting edge, the kind that disrupt industries and make people wonder how such things are even possible. That's my peak; that's where I always strive to be, to know as much as possible.

Question 2: Your Dream Job

The Question: What is your dream job right now? Describe it in detail. Is it Software Engineering, a specialty in AI, Research, or Engineering? What kind of problems do you want to solve, and which technologies do you most want to work with?

Answer:

That's an interesting question, and it's a bit hard for me to point to one specific role and make a final decision. However, I can definitely point to a field: the field of AI. It's a broad term, I know, but it contains several sub-domains that I've experimented with, and each one on its own has been very interesting and has piqued my curiosity.

I think what I most enjoy doing, on some level, is the research aspect—the R&D. I love trying to understand a new technology and then creating various POCs (Proofs of Concept) from it. I enjoy playing with the new tools, understanding what they can do, testing them, running tests, checking their limits, and running all sorts of wild experiments.

I've done this with AI in several directions:

Building Automations: Creating agents or workflows that use an AI API, like OpenAI, to perform various tasks.

Building Products: Creating an actual product that uses AI at its core to generate something.

Deep Dive: Getting deeply involved with the more technical aspects, like model weights, training models, and running models locally, which I've also had the chance to do.

I believe this entire spectrum is incredibly interesting to me, and I would love to specialize in any one of them. I'm open in this area to whoever gives me the opportunity. Ultimately, I think it all connects. If you're working with AI, you need to know how to touch on all these points to some degree. Where the main focus of my work would be depends on who would be willing to accept me and give me the chance. But I would still want to be involved in all of these aspects in one way or another.

Question 3: From the Start of Your Degree to Today

The Question: What is your professional story? How did you get from the beginning of your degree to where you are today? What motivated you to enter the AI field so strongly, in parallel with your work at Intel?

Answer:

As I started to say, from a young age, I loved to code, and I taught myself. I always loved technologies. Therefore, it was natural for me, without question, to go and study Computer Science. I went to the Open University because the ability to sit and learn by myself was both a strong suit of mine and very convenient for me.

In my second year, I joined Intel in a student position. I went to Intel because that's where I was accepted for the student role. The specific position...

Part 2: Professional Experience - Intel
Question 4: Team's Business Goal

The Question: What was the business goal of your team, Tools & Validation, at Intel? As part of the large puzzle that is Intel, what role did you fill?

Answer:

Okay, I can talk about this as much as you'd like. Here's how it works:

In the organization I am in, which is called SFP, we are responsible for a Security Engine that resides inside a chip called the PCH. Now, for this piece of firmware, there are many groups, and each group develops a different part of what is ultimately an image binary that is burned onto the chip. Each group is responsible for a different part.

The group I was assigned to is called Line Tools. This group, specifically, did not develop the firmware itself, although, in practice, we are considered firmware developers because we are under that same larger group. But the specific part of our team, the Line Tools, was responsible for developing tools—local tools that run on Linux, Windows, and in the UEFI environment for our customers. These tools are used for the Line Tools in the manufacturing process.

When they are running their tests and defining configurations within the PCH, in that engine, the Security Engine we work on, they interface with it through the Line Tools. So, our development was essentially those tools that create the communication, through the appropriate drivers, to the firmware. These tools configure it, set it up, perform tasks like "close manufacturing," and sign things. They have a significant role, but they don't run inside the firmware; rather, they communicate with the firmware.

These tools are written in C, for the most part, and they run on Linux, UEFI, and Windows.

Now, the teams within our group were divided. Each IP, like Line Tools, was split into two parts: a validation part and a development part.

When I first joined Intel, I was in the validation team. For most of my time there, my job was to define the test plan for new changes, new features, and new projects. For each of these, we had to define a new test plan and then develop the execution automation for it.

Ultimately, this was the main focus of our work. We worked in C#, we had a sort of Core Tester, and our job was to develop the flows—first to define the test flows and then to develop the automation in C# that would execute it.

This automation is supposed to run on a controller machine that is connected to a real machine with that same PCH, with the firmware we need to interface with burned onto it. Our automation knows how to perform the communication through some internal tool, to execute commands on the tools that are on the real machine, read the output, process it, check it, and perform various flows. Some flows are simple, like running a command and parsing the output, while others are more complex, where we need to bring the machine to a specific state, burn the firmware in a certain way, configure it, add keys related to cryptography, and more.

This requires a deep understanding of the firmware and how it works because, as the Line Tools team, we touch all the IPs and all the components in our SFP organization. Every team is responsible for a different part of the firmware, each creating some logic or feature, and the Line Tools needs to know how to interact with all of them. So, we end up needing to understand the entire process at a certain level to be able to test the tools properly.

So, that was our role: to create the test plan and the automation. The actual execution—running it and monitoring the logs—was done by a different group called Factory, which ultimately produces the execution itself. But, in the end, we were still responsible for the final sign-off. If there were failures, we had to investigate what was happening, sometimes manually, sometimes through the automation.

The environment was primarily development in the .NET ecosystem with C#. It's a large, complex system built with modules from our team and other groups, all integrating into flows and specific tests. There's a very large and broad infrastructure to make it all work.

Question 5: Team and Organizational Change

The Question: How many people were on the team? Describe the transition you made to the Core Firmware Tool Development team. Was this your initiative?

Answer:

The number of people on the team fluctuated; Intel has gone through changes. There were times we were more people, and times we were fewer. Right now, we are about four people.

What happened was an organizational change where they merged the teams. Instead of having a separate development team and a validation team, they combined us into one team. So now, we are not divided between validation and development; we are one team responsible for the Line Tools. This means we also get development tasks for the tools themselves, and the developers also get validation tasks.

So, my title is no longer Firmware Validation but rather Firmware Developer or Tools Developer. It's important to clarify this because, in the end, we are now a unified team. We are still in the process of this integration, slowly getting more familiar with the code and the development side, but it's an ongoing process.

The move was part of this organizational change, based on the understanding that it's better for the same team to handle both development and validation. This way, the team has a better understanding of the tools and, in turn, can perform better validation. It also helps us solve bugs and issues faster.

The new tasks I've taken on involve understanding how to compile, how the tool's code works (moving from C# to C), and how the build scripts in Python operate. For a new and complex project that involved a deep change in the tools' structure, I was involved with the Python scripts that configure variables and placeholders during the build process. That's how I started getting into the development side of things.

Part 3: AI Projects (Within Intel)
LLM Bug Classification Workflow

The Problem: Manually classifying bugs during our weekly "Sys-Debug" meeting was time-consuming. A group of managers and PMs would sit and go through each bug to determine its status, who is responsible for it, and what fields to update. The specific task I focused on was classifying the "Security Impact" field (Yes/No), which is a difficult and nuanced decision, especially for someone who isn't a security expert.

The Solution & Process: I developed a tool to automate this classification using an LLM. My process was a series of experiments to find the best approach:

Baseline (Zero-Shot): I started with a simple system prompt explaining the concept of security impact to the LLM. I would then feed it the bug's title, description, and comments and ask it to classify. This achieved about 80.14% accuracy.

Fine-Tuning (TF-IDF): I tried training a simple statistical model (TF-IDF). It gave poor results, around 77.75%, so I learned this wasn't the right path, but it was a valuable learning experience.

Fine-Tuning (Sentence Embeddings): I trained a sentence embedding model. This performed better, at about 85% accuracy.

Few-Shot RAG (The Winning Approach): This was the breakthrough. I created a large database of thousands of already-classified bugs, indexed them into a ChromaDB vector database, and created a RAG (Retrieval-Augmented Generation) system.

When a new bug comes in, the system searches the vector database for the most semantically similar bugs.

It retrieves a balanced set of examples (e.g., three "Yes" impact and three "No" impact).

These examples are fed to the LLM as a "few-shot" prompt along with the new bug.

This method boosted the accuracy to 91%. When looking at how often it correctly identified a "Yes" impact bug, the accuracy was 92.36%. For correctly identifying a "No" impact bug, it was an incredible 98.55%.

Outcome: I developed this into a feature within an internal tool called the "SFP Bot," which is a chatbot for our organization.

AI Codebase Assistant (RAG Agent)

The Problem: While models like GPT are great at general coding, they struggle with large, proprietary codebases. They don't know the context, the structure, or the specific logic.

The Solution: This project was for an internal hackathon. I led a team to build an "agent" that could answer questions about our codebase. The approach was different from a standard RAG on raw code:

Indexing/Summarization: Instead of just embedding raw code, we first ran a script with an LLM over the entire codebase. For each file, it generated a summary: what the file does, what functions it contains, etc. This was stored in a large JSON file.

Querying: When a user asks a question, the agent first consults this JSON "map" of the codebase to identify the most relevant files.

Answering: It then feeds the content of only those relevant files into the LLM's context window to generate the answer.

Outcome: The idea was promising, but it was hard to scale into a real product. Shortly after, tools like GitHub Copilot Agent emerged, which did this more effectively. Still, it was a great learning experience in building agentic workflows.

Part 4: Personal & Academic Projects
Motivation

The Question: For each personal project, what motivated you to build it? Was it technological curiosity, a desire to solve a personal problem, or the desire to learn a specific tool?

Answer:

It's a mix of all three. Sometimes I see a tool, I download it, clone the repository, and just start playing with it to see what I can change. Other times, it comes from a specific need.

Academic Paper Summarizer (A Personal Need): For a seminar paper in my academic studies, I had to read many research papers. This can be tedious, especially in a field like AI where there are many new and complex terms. So, I built a tool with a GUI where I could upload a PDF of a paper. The tool would use an LLM to break the paper down into topics and sub-topics, displayed in a neat list. I could click on any topic, and it would provide a clear, structured summary, with a chat option to ask follow-up questions. This made the process of understanding and writing about the papers much more manageable and organized.

Code Deep Research Agent (Technological Curiosity): This was about playing with an open-source tool that used a feedback loop for deep research. It would generate search queries, get results, summarize them, and decide if it needed to search for more. I adapted this idea to work on a local codebase. Instead of a search engine, it would query an indexed version of the code. The idea was to create a system that could deeply understand a local codebase. While the results weren't perfect, the process was fascinating.

Local AI and Automation: I love running models locally on my own machine. I run Ollama models, use tools like ComfyUI for image generation, and have set up automations with n8n. For example, I have a workflow that scrapes AI news every morning, uses Google's text-to-speech to create a mini-podcast, and sends it to my Telegram. It's a fun, useful project that I use daily.

Academic Projects

Secure Network App: This was a university project where we had to create a secure client-server application. The server was in C++, the client in Python, and they communicated over sockets. The process involved a secure key exchange on the first connection and then encrypting/decrypting messages for all subsequent communication.

Compiler Project: A large and interesting project in C where we built a compiler for a language that compiled down to Assembly.

Part 5: Skills, Abilities, and Traits
Programming Languages

Below are the languages you mentioned. Please rate your proficiency (1-5) and note which you feel most at home with.

C#: 4/5. This is the language I use most in my day job at Intel. The automation framework is written in C#, so I spend a lot of time reading, debugging, and writing code within it.

Python: 4.5/5. I feel most at home with Python. When I want to build something for myself, Python is my go-to. It's fast, simple, and the ecosystem is perfect for the AI and automation projects I love. All my personal projects, from the RAG systems to the various agents, are built in Python.

C/C++: 3/5. I have experience with it from university projects and from reading the Line Tools code at work, but it's not my primary language for development.

AI/ML Skills

Below are the concepts you mentioned. Briefly describe a project where you used each.

RAG (Retrieval-Augmented Generation):

Project: The LLM Bug Classification Workflow. I built a RAG system that retrieves semantically similar, pre-classified bugs from a ChromaDB vector database to provide few-shot examples to the LLM, significantly improving its classification accuracy.

Fine-Tuning & LoRA:

Project: My personal research project on fine-tuning a model for the Line Tools IP. I experimented with full fine-tuning and LoRA to teach a smaller model the specifics of our domain. This involved learning about the entire process: creating an augmented dataset, using tools like Axolotl, and understanding the difference between full fine-tuning and parameter-efficient methods like LoRA.

Vector Databases (ChromaDB, Faiss):

Project: Used ChromaDB in the Bug Classification project to store and retrieve bug embeddings. Used Faiss in the Code Deep Research project for in-memory vector searches. My understanding is that ChromaDB is excellent for persistent storage with filtering capabilities, which was crucial. For example, I needed to filter the search space before running the similarity search, a feature ChromaDB supports well.

LangChain & Agents:

Project: The AI Codebase Assistant. I used LangChain to structure the agentic workflow. While I find myself using its core components (like prompt templates and output parsers) more than the high-level agent frameworks, it's a foundational tool for nearly all my AI projects. The JSONStructureOutputParser is particularly useful for forcing models to return structured, reliable data.

Key Abilities

Problem Solving:

Example: The technical challenge with Secure Boot at Intel. When tasked with validating a new tool signature, no one in my immediate team knew the full process for enabling Secure Boot and injecting the necessary keys. I had to dig through obscure internal repositories, contact teams in Germany, and piece together the entire workflow. I ended up scripting the process of injecting keys into the firmware image before it was burned, which allowed me to run the validation successfully. The challenge wasn't just running a command; it was the entire ecosystem of research and experimentation around it.

Proactive Learning (Autodidactic):

Example: The entire field of AI. Fine-tuning, RAG, vector databases—these were not things I learned in a formal course. I learned them by myself through YouTube, articles, documentation, and hands-on experimentation. When I decided I wanted to learn fine-tuning, I set up a powerful local machine with two RTX 3090s and dove in, learning everything from data preparation to the training process itself.

Automation Philosophy:

Mantra: "To do: Automate everything. If it can't be automated, make it automatable."

Example: The fine-tuning workflow itself. I quickly realized that running experiments with different parameters was tedious. So I built a workflow using an LLM to manage the process. The LLM would read the dataset, suggest a configuration, run the fine-tuning, test the resulting model, and then, based on the results, suggest a new configuration for the next run. It was an automation loop designed to optimize the process of creating another automation. This is my philosophy in a nutshell.

If you have any more questions, feel free to ask.