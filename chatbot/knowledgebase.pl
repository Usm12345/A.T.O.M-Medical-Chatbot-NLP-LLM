% Gender facts
male(ali).
male(bob).
male(jack).
female(alia).
female(tahira).
female(sara).
female(mary).

% Marriage facts
married(ali, tahira).
married(jack, sara).
married(bob, mary).

% Age facts
age(ali, 60).
age(tahira, 58).
age(jack, 40).
age(sara, 38).
age(bob, 45).
age(mary, 43).

% Family relationships
parent(ali, bob).
parent(tahira, bob).
parent(jack, alia).
parent(sara, alia).

% Death facts
died(jack).

% Foster relationships
foster_parent(ali, mary).
foster_parent(tahira, mary).

% Rules
% Aunt: An aunt is the sister of a parent.
aunt(Aunt, Child) :-
    female(Aunt),
    parent(Parent, Child),
    sibling(Aunt, Parent).

% Sibling relationship
sibling(X, Y) :-
    parent(P, X),
    parent(P, Y),
    X \= Y.

% Uncle: An uncle is the brother of a parent.
uncle(Uncle, Child) :-
    male(Uncle),
    parent(Parent, Child),
    sibling(Uncle, Parent).

% Widow: A widow is a woman whose husband has died.
widow(Woman) :-
    female(Woman),
    married(Woman, Husband),
    died(Husband).

% Foster_child: A foster child is a child who is not the biological child of a parent but is raised by them.
foster_child(Child, Parent) :-
    foster_parent(Parent, Child).

% Mother_in_law: The mother-in-law of a person is the mother of their spouse.
mother_in_law(MIL, Person) :-
    married(Person, Spouse),
    parent(MIL, Spouse),
    female(MIL).
