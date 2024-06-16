% Define individuals
male(ali).
male(ahmad).
male(asad).
female(samra).
female(hiba).
female(sadia).

% Define parent relationships
parent(ahmad, ali).
parent(asad, ahmad).
parent(samra, ali).
parent(hiba, ali).
parent(sadia, samra).

% Define spouse relationship
spouse(ali, hiba).

% Define grandparent relationship
grandparent(sadia, ali).

% Define sibling relationship
sibling(X, Y) :-
    parent(Z, X),
    parent(Z, Y),
    X \= Y.

% Define mother relationship
mother(X, Y) :-
    female(X),
    parent(X, Y).

% Define father relationship
father(X, Y) :-
    male(X),
    parent(X, Y).
