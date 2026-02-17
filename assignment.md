Project 1

Grading and Submission Policies: Project 1 will contribute to the class grade as specified in the syllabus. All students must submit for Project 1 using the appropriate link in the Quizzes website area, and using the submission naming convention specified further down on this page. If you want just one group member to submit your submission, the other team members have to at least submit some text with a pointer to the submitting student in their team.

The project should be realized by a team of, ideally, 2 or 3 students (well motivated exceptions for 1-student or 4-student teams will be likely accepted). Each team has to detail which tasks were done by which student. The implementation can be in any programming language, but it is strongly recommended to use Python to help us with automated testing, if any, of your submission. The project comes with a minimal assignment and requires a submission of both software and a report being graded mainly by the TAs according to scoring criteria defined below; any additional work you perform might be considered extra credit work if later also submitted as a response to the Extra Credit assignment in the Quizzes website area.  

Project 1

Topic: Design of multi-party one-time pad secured communication protocols for asynchronous networks

Introduction

This problem asks for new approaches to develop efficient multi-party communication protocols for applications like collaborative, multi-party, communication (e.g., conferencing, instant messaging, chat rooms), satisfying perfect secrecy. 

The problem is based on content from Lecture 1 and is related to (not needed) content from Lecture 5.

Preliminaries

You have learned that Alice can send to Bob a message with perfect secrecy using the one-time pad encryption scheme.

For multiple messages from either party, this scheme requires Alice and Bob to agree in advance on a sequence of pads to be used for later messages. To avoid reusing pads, which would result in loss of message secrecy, they can agree on a sequence of pads, use as much as they can of it, then agree on a new sequence, and so on. Agreeing is the most expensive part of this process and so should be done as rarely as possible. In other words, they should be using as many pads as possible in every agreed sequence, again without reusing any pad. But, at agreement time, they may not know who of them is going to send messages in the future, and how many pads do those messages require. Moreover, in practical networks like the Internet, there can be communication delays, and there is a chance that Alice and Bob use the same pad p, as follows: one party uses p, and the communication related to p is delayed; the other party uses p thinking that p has not been used (while instead it was used and its related communication was delayed). This would violate the perfect secrecy of messages. 

One solution to avoid this problem is that Alice and Bob continuously agree on who is the next sender and then only the next sender uses the next unused pads; this solution is ruled out as impractical for various reasons (for instance, it is expensive in terms of communication and computation time performed during each agreement phase). 

Another solution consists of Alice and Bob splitting the pad sequence in 2 equal halves, each party only using one of the two halves. No matter what is the sending schedule (i.e., no matter what is the sequence of parties sending messages), this solution can never waste more than half of the pads, the worst case scenario being when only one of the two parties sends messages, and so the other half of the pads in the sequence goes wasted. 

Here, a natural question is if we can reduce the number of wasted pads, perhaps assuming that at any given time, no more than d undelivered messages (each message of length = 1 pad) are in the network, for some small value d (in particular, smaller than n/2, where n is the sequence length). It turns out that we can. Alice can use pads 1,2,3,... as needed, and Bob can use pads n, n-1, n-2,..., as needed, with the constraints that Alice uses the next pad if and only if some undelivery secrecy condition is satisfied (e.g.: |last_used_pad_index(Bob) - last_used_pad_index(Alice)| > d), and similarly does Bob. No matter what is the sending schedule (i.e., no matter what is the sequence of parties sending messages), this solution wastes no more than d pads. Moreover, this solution can be proved to be optimal in the following sense: if there were a protocol wasting strictly less than d pads (for -all- usage schedules), you could show that such a protocol does not satisfy perfect secrecy, because there may be a sending schedule on which a pad is used by both. 

Main questions:

Design, document and evaluate an m-party protocol for the same problem, in the case m = 3 or 4 (only pick one), where each party sends a message to all other m-1 parties, your goal being that of (1) maintaining perfect secrecy (i.e., no pad is used twice by the same or different parties); (2) your protocol wastes a small number of pads, given an arbitrarily ordered sequence of messages from the m parties; (3) a party's runtime to send a message is not too large (i.e., ideally constant with respect to L, but solutions with runtime linear in L wasting less pads are also of interest). You can assume, for simplicity, that the network delivers each message at the same time to all m-1 parties (but different messages can take different delivery times). Can your solution waste less than ((m-1)/m)*n pads? In other words, is your solution better than the obvious protocol where the pad sequence is split into m equal and disjoint parts and each party only uses exactly one of these parts? Please note that any protocol must waste at least d pads, in the sense that if there were a protocol wasting less than d pads (for all usage schedules), it would not satisfy perfect secrecy.

You need to test your solution by measuring its (average) number of wasted pads in the following scenarios (here, L denotes the length of a single pad in the shared n-pad sequence):

(Scenario (S.x)): only x, randomly chosen, parties repeatedly send L-length messages, where the decision of who sends the next message is also randomly chosen. Use x=1,2,3 if you chose m=3, or x=1,2,4 if you chose m=4.

In your solution test, you could calculate the average number of unused pads in a pad sequence, the average being taken across several protocol executions, and where a protocol execution is defined to end whenever at least one party cannot send the next message securely. In each protocol execution, you only need to use a single pad sequence.

If you think of more than one approach for your protocol design, you have to combine them into a single approach, as only a single approach per team can be evaluated. (Or work with one main approach and only briefly describe any other approaches to make them count as extra credit material.)  

Your accompanying report should at least include the following sections:

1. Title of your project (based on your approach); something like "<chosen value of m>-Party Asynchronous Communication with Perfect Secrecy based on <main approach idea name>".

2. An introduction section containing the following: team member names; list of project tasks performed by each student in the team; which value of m you chose; a very concise description of the main claims:

a. the number of wasted pads in the above scenarios S.x, and the maximum number of wasted pads across all possible usage schedules);

b. a party's runtime to send a single message;

these can be expressed as a function of the number m of parties, the length n of the pad sequence, the undelivery parameter d, as well as any other parameters you introduce.

If you ended up simplifying the problem, you should clearly state all modifications you made with respect to the above specifications.

3. A detailed informal explanation (using much more English than pseudo-code) of the design of your submission's protocol  

4. A detailed rigorous description (using much more pseudo-code than English) of the design of your submission's protocol  

5. A proof or proof intuition that your solution has the claimed number of wasted pads in the scenarios S.x and with respect to all possible usage schedules

6. Readme-like information to run your submission's protocol program (in, say, Python, Rust, C, etc.)

7. Readme-like information to run your submission's testing program (in, say, Python, Rust, C, etc.).


Extra credit topics can be:

ec1: generalize your solution to one of the values of m in {3,4} that you had not chosen

ec2: generalize your solution to any m smaller than n/d.


Submission conventions and grading criteria:

Your submission can be a zip file (not a link to a github repository), submitted on this website, in the appropriate space under Quizzes, containing at least the following files:

project report (in pdf form)
protocol code
testing code.
All of these files (including any requirements.txt file) need to be in the top directory (as opposed to some subdirectory).

You must name your zip file as (assuming a team of 3 students here): <last-name1><last-name2><last-name3>-AppCrySp26Project1 and your contained files as

<last-name1><last-name2><last-name3>-<chosen value of m>-report
<last-name1><last-name2><last-name3>-<chosen value of m>-protocol
<last-name1><last-name2><last-name3>-<chosen value of m>-testing.
Your submission will be judged based on the following grading criteria:

software correctness and usability (i.e., if you followed all of the above instructions, if software runs correctly, and is easy to use)
quality of report (i.e., how well written is your report)
how interesting is your protocol approach (i.e., in terms of novelty of the ideas used in your algorithm) or/and how successful is your protocol in terms of wasting a small number of pads (the higher m the more valuable your solution is)  
A protocol design which is either somewhat interesting or somewhat successful will be rewarded with a score at least at the B or B+ level. A protocol design which is either very interesting or very successful will be rewarded with a score at least at the A- level. A protocol design which is either very interesting and somewhat successful, or somewhat interesting and very successful will be rewarded with a score in the A level. The problem for m=4 is somewhat harder than the problem for m=3 and this also will be taken into account.

Use of publicly available documents, software libraries, and/or AI tools is allowed (if in respect of their licenses and if this use is properly documented in your report) and might affect your submissions' score in that the instructor will judge how valuable is your contribution to your solution, after knowledge of your used documents, software libraries and AI tools. Undocumented use of publicly available documents, software libraries and/or AI tools would be a reason for score reduction and may even trigger a plagiarism event.

The top team(s) will be announced and rewarded with extra credit if they later record a short video with a presentation of their strategy.

Due date is on the syllabus. No late submissions can be accepted without score penalty depending on how late you are, and early submissions are encouraged. You are strongly recommended to submit any questions to the TAs (see Syllabus content area for their contact info) and to the instructor.