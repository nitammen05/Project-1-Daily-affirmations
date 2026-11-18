Rules for programming:

1. Only write in Python  
2. Do not edit or delete original files  
3. The program should be runnable from a terminal  
4. The program should have tests after and during the implementation of every method, function, or function to make sure it runs properly  
5. Do not ask me any questions about how to implement the project, as long as it works, its good   
6. You may make your own REASONABLE decisions

Standing rules for every session (added 2026-11-13):

7. Never undo or amend a commit (no `git commit --amend`, `git reset`, `git revert`, or force-push). Fix mistakes with a new commit.
8. Use only the Python standard library. Write tests with `unittest` (pytest is not installed). Run them with `python3 -m unittest discover -s tests -t . -v`.
9. Never delete, reset, or commit the runtime data files `affirmations.txt`, `ratings.json`, `calm_music.wav`. They hold my real data. Tests must use a temporary directory.
10. When you make an implementation choice I did not ask for, add it to `decisions.md` with the reason.
11. At the end of a round, write `handoff-round-<N>.md` for the next session. Do not commit handoff files or changes to `CLAUDE.md`; I read and edit them first.
