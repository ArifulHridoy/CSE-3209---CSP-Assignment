# UEFA Champions League (UCL 2026/27) Draw - Constraint Satisfaction Problem (CSP)

## 📌 Problem Overview
This project models and solves the **UEFA Champions League (UCL 2026/27)** 32-team classic group stage draw as a **Constraint Satisfaction Problem (CSP)** in Artificial Intelligence.

In this tournament format:
- **32 European clubs** are qualified and distributed into **4 Seeding Pots** (Pot 1, Pot 2, Pot 3, Pot 4) containing **8 teams each**, based on domestic league championships and UEFA club coefficient rankings.
- The 32 clubs must be assigned into **8 Groups** (Group A to Group H), with **4 teams per group**.
- The draw must satisfy strict UEFA operational, sporting, and television broadcasting constraints.

---

## 🏆 The 32 Qualified Teams & Seeding Pots (2026/27 Simulation)

| Pot | Club | Country / League | Seeding Criterion |
| :---: | :--- | :---: | :--- |
| **Pot 1** | Real Madrid | ESP | UCL Title Holder / #1 UEFA Coefficient |
| **Pot 1** | Manchester City | ENG | Premier League Champion / #2 UEFA Coefficient |
| **Pot 1** | Bayern Munich | GER | Bundesliga Champion / #3 UEFA Coefficient |
| **Pot 1** | Paris Saint-Germain | FRA | Ligue 1 Champion / #5 UEFA Coefficient |
| **Pot 1** | Inter Milan | ITA | Serie A Champion / #6 UEFA Coefficient |
| **Pot 1** | Bayer Leverkusen | GER | German Champions / Top 15 Coefficient |
| **Pot 1** | Sporting CP | POR | Primeira Liga Champion |
| **Pot 1** | PSV Eindhoven | NED | Eredivisie Champion |
| **Pot 2** | Liverpool | ENG | Top 5 Club Coefficient |
| **Pot 2** | Arsenal | ENG | High Club Coefficient |
| **Pot 2** | Barcelona | ESP | Top 10 Club Coefficient |
| **Pot 2** | Atletico Madrid | ESP | Top 15 Club Coefficient |
| **Pot 2** | Borussia Dortmund | GER | UCL Finalist / Top 10 Coefficient |
| **Pot 2** | Juventus | ITA | High Club Coefficient |
| **Pot 2** | Atalanta | ITA | UEL Title Holder / Top 20 Coefficient |
| **Pot 2** | Benfica | POR | Top 20 Club Coefficient |
| **Pot 3** | RB Leipzig | GER | Top 20 Club Coefficient |
| **Pot 3** | AC Milan | ITA | High Club Coefficient |
| **Pot 3** | Feyenoord | NED | High Club Coefficient |
| **Pot 3** | Club Brugge | BEL | Belgian Champion |
| **Pot 3** | Shakhtar Donetsk | UKR | Ukrainian Champion |
| **Pot 3** | Red Bull Salzburg | AUT | Austrian Champion |
| **Pot 3** | Dinamo Zagreb | CRO | Croatian Champion |
| **Pot 3** | Lille | FRA | High Club Coefficient |
| **Pot 4** | Chelsea | ENG | European Contender |
| **Pot 4** | Girona | ESP | Spanish Qualifier |
| **Pot 4** | Monaco | FRA | French Qualifier |
| **Pot 4** | Celtic | SCO | Scottish Champion |
| **Pot 4** | Galatasaray | TUR | Turkish Champion |
| **Pot 4** | Red Star Belgrade | SRB | Serbian Champion |
| **Pot 4** | Young Boys | SUI | Swiss Champion |
| **Pot 4** | Sparta Prague | CZE | Czech Champion |

---

## 🎯 Formal CSP Formulation

### 1. Variables ($X$)
$$X = \{t_1, t_2, \dots, t_{32}\}$$
Each variable represents one of the 32 participating football clubs.

### 2. Domains ($D$)
$$D(t_i) = \{1, 2, 3, 4, 5, 6, 7, 8\} \quad \forall t_i \in X$$
Where $1$ to $8$ correspond to **Groups A, B, C, D, E, F, G, and H**.

### 3. Constraints ($C$)

1. **Pot Exclusivity (Sporting Balance)**:
   Every group must contain exactly one club from Pot 1, Pot 2, Pot 3, and Pot 4.
   $$\forall u, v \in \text{Pot}_k \text{ with } u \ne v \implies \text{Group}(u) \ne \text{Group}(v)$$

2. **Country / League Protection (Domestic Separation)**:
   No two clubs from the same national association/domestic league can be drawn into the same group.
   $$\forall u, v \in \text{League}_m \text{ with } u \ne v \implies \text{Group}(u) \ne \text{Group}(v)$$

3. **Television / Calendar Pairing (Red vs. Blue Groups)**:
   Groups 1–4 (A–D, "Red") play on one matchday (e.g. Tuesday), while Groups 5–8 (E–H, "Blue") play on the other matchday (Wednesday).
   Clubs paired for domestic broadcasting from the same nation (e.g., Real Madrid & Barcelona, Man City & Liverpool, Bayern & Dortmund) cannot be placed in the same color group set:
   $$\text{Half}(\text{Group}(u)) \ne \text{Half}(\text{Group}(v)) \quad \forall (u, v) \in \text{TV\_Pairs}$$

---

## 🧠 AI Heuristics Implemented

- **Backtracking Search**: Depth-first exploration with systematic pruning.
- **Minimum Remaining Values (MRV)**: Selects the unassigned club with the smallest remaining domain of valid groups to fail-first and minimize the search tree branching factor.
- **Degree Heuristic**: Breaks ties in MRV by selecting the club involved in the highest number of constraints with other unassigned clubs.
- **Least Constraining Value (LCV)**: Orders group assignments by selecting the group that rules out the fewest options for neighboring unassigned clubs.
- **Forward Checking & AC-3**: Propagates constraints immediately after each assignment, pruning illegal groups from affected clubs' domains and triggering immediate backtracks if any club's domain becomes empty.

---

## 💻 How to Run

Ensure Python 3 is installed:

```bash
# Navigate to directory
cd UCL-2026-27-CSP

# Execute solver
python ucl_csp.py
```

### Input File Format (`input.txt`)
```text
<GROUP COUNT>
<POT COUNT>
<Pot 1 comma-separated teams>
<Pot 2 comma-separated teams>
<Pot 3 comma-separated teams>
<Pot 4 comma-separated teams>
<LEAGUE_CODE>:<team1>,<team2>,...
...
```

### Output File Format (`output.txt`)
```text
Yes
<group 1 teams comma-separated>
<group 2 teams comma-separated>
...
<group 8 teams comma-separated>
```
*(No trailing newline at end of file, conforming to the grading standard).*
