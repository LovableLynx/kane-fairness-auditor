"""Name pools for CV twins.

First names and surnames follow the correspondence-study design of
Bertrand & Mullainathan (2004), "Are Emily and Greg More Employable than
Lakisha and Jamal?", American Economic Review 94(4). Those names were chosen
in that study because they are strongly associated with a perceived race and sex;
we reuse them only to construct synthetic test CVs.

Group labels are kept neutral ("A" / "C") so they line up with the
FairCVdb ethnicity groups used to train the demo models.
"""

FIRST = {
    ("female", "A"): ["Allison", "Anne", "Carrie", "Emily", "Jill", "Laurie", "Kristen", "Meredith", "Sarah"],
    ("female", "C"): ["Aisha", "Ebony", "Keisha", "Kenya", "Lakisha", "Latonya", "Latoya", "Tamika", "Tanisha"],
    ("male", "A"): ["Brad", "Brendan", "Geoffrey", "Greg", "Brett", "Jay", "Matthew", "Neil", "Todd"],
    ("male", "C"): ["Darnell", "Hakim", "Jamal", "Jermaine", "Kareem", "Leroy", "Rasheed", "Tremayne", "Tyrone"],
}

LAST = {
    "A": ["Baker", "Kelly", "McCarthy", "Murphy", "Murray", "O'Brien", "Ryan", "Sullivan", "Walsh"],
    "C": ["Jackson", "Jones", "Robinson", "Washington", "Williams"],
}

PRONOUNS = {
    "male": {"subj": "He", "obj": "him", "poss": "his"},
    "female": {"subj": "She", "obj": "her", "poss": "her"},
}

# Reverse lookups used by targets that (wrongly) infer demographics from a CV.
FIRST_TO = {n: key for key, names in FIRST.items() for n in names}
LAST_TO = {n: grp for grp, names in LAST.items() for n in names}
