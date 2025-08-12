## This script based on NoSQL injection on TryHackMe. Automating script to brute-force the password in Task 6. we can smash through that THM NoSQL lab without Burp Intruder’s slow grind.

<img width="1218" height="256" alt="nosql2" src="https://github.com/user-attachments/assets/e82a2628-e81c-4066-a5d6-afae80c4588e" />

This script,
1. Automatically detecting the password length using regex patterns.

2. Brute-forcing the password character-by-character by leveraging regex matching on the server’s login endpoint.
(In this attack, we’re not brute-forcing the whole password at once.Instead, we guess one character at a time, always matching a prefix of the password with a regex.)
3. Saving progress to resume the attack if interrupted.

4. Providing an estimated time remaining (ETA) for the attack completion.

<img width="1092" height="365" alt="nosqli" src="https://github.com/user-attachments/assets/86dbc596-dddb-45f1-98f4-cc751bc3d7f3" />
