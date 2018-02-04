# Clew Logic

Solving Clue© with set-based logic.

Use SAT solver

6, 6, 9

324 possible combinations

[1, 2, 3, 4, 5, 6]
[7, 8, 9, 10, 11, 12]
[13, 14, 15, 16, 17, 18, 19, 20, 21]

[[1, 8, 13], [-1, -2, 3, 4], [18, 7, 6, -3]...]

### Initial Clauses

Each card is in at least one place

Each card is in exactly one place; for each pair of places, a card cannot be in both
!(p1 and p2) !p1 or !p2

A least one card of EACH category is in the case file

No two cards of ONE category is in the case file

### Suggestion

Players between suggester and answerer do not have the cards

Answerer has one of the cards

If suggester is current player, then answerer has the card shown

If no answerer, either the suggester or the solution has the cards
