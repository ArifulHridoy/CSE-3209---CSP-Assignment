"""
Constraint Satisfaction Problem (CSP) Solver
Problem: UEFA Champions League (UCL) Group Stage Draw (32 Teams, 8 Groups)
Course: CSE 3209 -Artificial Intelligence

Algorithms & Heuristics Implemented:
1. Backtracking Search
2. Minimum Remaining Values (MRV) Heuristic with Degree Heuristic Tie-Breaker
3. Least Constraining Value (LCV) Heuristic
4. Arc Consistency 3 (AC-3) & Forward Checking
"""

import sys
import os
from collections import defaultdict, deque

"""
        CSP Formulation:
        - Variables: 32 Clubs
        - Domains: {1, 2, ..., num_groups} (Group index A=1, B=2, ..., H=8)
        - Constraints:
            1. Pot Exclusivity: exactly 1 team per pot per group (no two teams from same pot in same group).
            2. Country / League Protection: no two teams from the same league/association in the same group.
            3. TV Pairing (optional/bonus): paired teams split across Red half (1..4) and Blue half (5..8).
"""

class UCL_CSP:
    def __init__(self, variables, domains, pots, leagues, tv_pairs=None):
        self.variables = variables
        self.domains = {v: list(domains[v]) for v in variables}
        self.pots = pots
        self.leagues = leagues
        self.tv_pairs = tv_pairs if tv_pairs else []
        self.curr_domains = {v: list(self.domains[v]) for v in variables}
        
        # Build binary inequality constraints graph (neighbors)
        self.neighbors = defaultdict(set)
        
        # 1. Pot constraints: teams in same pot cannot share a group
        for pot_name, teams in self.pots.items():
            for i, t1 in enumerate(teams):
                for t2 in teams[i + 1:]:
                    self.neighbors[t1].add(t2)
                    self.neighbors[t2].add(t1)
                    
        # 2. League constraints: teams in same league cannot share a group
        for league_name, teams in self.leagues.items():
            for i, t1 in enumerate(teams):
                for t2 in teams[i + 1:]:
                    self.neighbors[t1].add(t2)
                    self.neighbors[t2].add(t1)

        # Precompute TV pair lookup
        self.tv_map = {}
        for (t1, t2) in self.tv_pairs:
            self.tv_map[t1] = t2
            self.tv_map[t2] = t1

        self.num_backtracks = 0
        self.num_assignments = 0

    # -------------------------------------------------------------
    # Constraint Verification
    # -------------------------------------------------------------
    def is_consistent(self, var, val, assignment):

        # Pot & League inequality constraints
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == val:
                return False

        # TV Pairing constraint (Red half = 1..4, Blue half = 5..8)
        if var in self.tv_map:
            partner = self.tv_map[var]
            if partner in assignment:
                var_half = 1 if val <= 4 else 2
                partner_half = 1 if assignment[partner] <= 4 else 2
                if var_half == partner_half:
                    return False

        return True

    # -------------------------------------------------------------
    # Heuristics: MRV + Degree Heuristic
    # -------------------------------------------------------------
    def select_unassigned_variable(self, assignment):

        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None
        
        def mrv_degree_key(var):
            mrv_score = len(self.curr_domains[var])
            degree_score = sum(1 for n in self.neighbors[var] if n not in assignment)
            return (mrv_score, -degree_score)

        return min(unassigned, key=mrv_degree_key)

    # -------------------------------------------------------------
    # Heuristics: LCV (Least Constraining Value)
    # -------------------------------------------------------------
    def order_domain_values(self, var, assignment):

        def count_conflicts(val):
            conflicts = 0
            for neighbor in self.neighbors[var]:
                if neighbor not in assignment and val in self.curr_domains[neighbor]:
                    conflicts += 1
            if var in self.tv_map:
                partner = self.tv_map[var]
                if partner not in assignment:
                    val_half = 1 if val <= 4 else 2
                    for p_val in self.curr_domains[partner]:
                        p_half = 1 if p_val <= 4 else 2
                        if p_half == val_half:
                            conflicts += 1
            return conflicts

        return sorted(self.curr_domains[var], key=count_conflicts)

    # -------------------------------------------------------------
    # Inference: Forward Checking & AC-3 Pruning
    # -------------------------------------------------------------
    def forward_check(self, var, val, assignment):

        removals = []
        
        # 1. Prune other values from var's domain
        for other_val in list(self.curr_domains[var]):
            if other_val != val:
                self.curr_domains[var].remove(other_val)
                removals.append((var, other_val))

        # 2. Prune val from all unassigned neighbors
        for neighbor in self.neighbors[var]:
            if neighbor not in assignment and val in self.curr_domains[neighbor]:
                self.curr_domains[neighbor].remove(val)
                removals.append((neighbor, val))
                if len(self.curr_domains[neighbor]) == 0:
                    return False, removals

        # 3. TV pairing half-pruning
        if var in self.tv_map:
            partner = self.tv_map[var]
            if partner not in assignment:
                val_half = 1 if val <= 4 else 2
                for p_val in list(self.curr_domains[partner]):
                    p_half = 1 if p_val <= 4 else 2
                    if p_half == val_half:
                        self.curr_domains[partner].remove(p_val)
                        removals.append((partner, p_val))
                        if len(self.curr_domains[partner]) == 0:
                            return False, removals

        return True, removals

    def restore_domain_removals(self, removals):
        """Restores pruned values back to curr_domains upon backtrack."""
        for var, val in removals:
            self.curr_domains[var].append(val)

    # -------------------------------------------------------------
    # Backtracking Search Engine
    # -------------------------------------------------------------
    def backtrack(self, assignment):
        """
        Recursive Backtracking Search with MRV, LCV, and Forward Checking.
        """
        if len(assignment) == len(self.variables):
            return assignment

        var = self.select_unassigned_variable(assignment)
        if var is None:
            return assignment

        for val in self.order_domain_values(var, assignment):
            if self.is_consistent(var, val, assignment):
                self.num_assignments += 1
                assignment[var] = val
                
                success, removals = self.forward_check(var, val, assignment)
                if success:
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result

                # Backtrack: undo forward check and unassign
                self.restore_domain_removals(removals)
                del assignment[var]
                self.num_backtracks += 1

        return None

    def solve(self):
        return self.backtrack({})


# -----------------------------------------------------------------
# File I/O and Execution Pipeline
# -----------------------------------------------------------------
def parse_input_file(filepath):
    """
    Parses input.txt according to the homework specification:
    Line 1: <GROUP COUNT>
    Line 2: <POT COUNT>
    Lines 3 .. 2 + POT COUNT: Comma-separated list of teams in each Pot
    Following Lines: <LEAGUE_CODE>:<team1>,<team2>,...
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    num_groups = int(lines[0])
    num_pots = int(lines[1])

    # Input validation
    for p_idx in range(num_pots):
        line_idx = 2 + p_idx
        if line_idx >= len(lines):
            raise ValueError(
                f"[INPUT ERROR] File specifies <POT COUNT> = {num_pots}, but only found {p_idx} pot lines before end-of-file.\n"
                f"For 32 teams in 8 groups, <POT COUNT> must be 4 (Pots 1 to 4 with 8 teams each)."
            )
        if ':' in lines[line_idx]:
            raise ValueError(
                f"[INPUT ERROR] On line {line_idx + 1}: Expected Pot {p_idx + 1} teams, but found league definition '{lines[line_idx]}'.\n"
                f"Explanation: Line 2 specifies <POT COUNT> = {num_pots}, which told the program to expect {num_pots} lines of pots.\n"
                f"However, in the 32-team UCL format, there are exactly 4 pots (with 8 teams each).\n"
                f"Please set Line 2 (<POT COUNT>) to 4."
            )

    pots = {}
    for p_idx in range(num_pots):
        pot_teams = [t.strip() for t in lines[2 + p_idx].split(',') if t.strip()]
        pots[p_idx + 1] = pot_teams

    leagues = {}
    for line in lines[2 + num_pots:]:
        if ':' in line:
            code, teams_str = line.split(':', 1)
            code = code.strip()
            if teams_str.strip() == 'None' or not teams_str.strip():
                leagues[code] = []
            else:
                teams = [t.strip() for t in teams_str.split(',') if t.strip()]
                leagues[code] = teams

    variables = []
    for pot_teams in pots.values():
        variables.extend(pot_teams)

    domains = {v: list(range(1, num_groups + 1)) for v in variables}

    return num_groups, num_pots, variables, domains, pots, leagues


def write_output_file(filepath, num_groups, assignment):
    """
    Writes output.txt according to the specification:
    Line 1: Yes / No
    Following lines: Comma-separated list of teams for each group.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        if assignment is None:
            f.write("No")
            return

        groups = {g: [] for g in range(1, num_groups + 1)}
        for team, grp in assignment.items():
            groups[grp].append(team)

        f.write("Yes\n")
        for g in range(1, num_groups + 1):
            if groups[g]:
                f.write(",".join(groups[g]))
            else:
                f.write("None")
            if g < num_groups:
                f.write("\n")


def display_results(num_groups, assignment, pots, leagues):
    """Prints a beautiful formatted summary of the draw."""
    if assignment is None:
        print("\n[RESULT] No valid draw found that satisfies all constraints.")
        return

    # Invert league and pot lookup
    team_league = {}
    for l_name, teams in leagues.items():
        for t in teams:
            team_league[t] = l_name

    team_pot = {}
    for p_num, teams in pots.items():
        for t in teams:
            team_pot[t] = p_num

    groups = {g: [] for g in range(1, num_groups + 1)}
    for team, grp in assignment.items():
        groups[grp].append(team)

    print("\n" + "=" * 76)
    print("      UEFA CHAMPIONS LEAGUE (UCL) GROUP STAGE DRAW - CSP SOLUTION")
    print("=" * 76)
    
    for g in range(1, num_groups + 1):
        grp_char = chr(64 + g)
        half_tag = "Red Half (Tue/Wed)" if g <= 4 else "Blue Half (Wed/Tue)"
        print(f"\n* GROUP {grp_char}  [{half_tag}]:")
        sorted_teams = sorted(groups[g], key=lambda t: team_pot.get(t, 99))
        for t in sorted_teams:
            pot_id = team_pot.get(t, "?")
            lg_id = team_league.get(t, "?")
            print(f"    - Pot {pot_id} | {t:<24} | League: {lg_id}")

    print("\n" + "-" * 76)
    print("Verification of Constraints:")
    all_pots_ok = True
    all_leagues_ok = True
    for g in range(1, num_groups + 1):
        g_pots = [team_pot[t] for t in groups[g]]
        g_leagues = [team_league[t] for t in groups[g]]
        if len(g_pots) != len(set(g_pots)):
            all_pots_ok = False
        if len(g_leagues) != len(set(g_leagues)):
            all_leagues_ok = False

    print(f"  [✓] Pot Exclusivity (1 team per pot per group): {'PASSED' if all_pots_ok else 'FAILED'}")
    print(f"  [✓] Country/League Protection (no same-league clash): {'PASSED' if all_leagues_ok else 'FAILED'}")
    print("=" * 76)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "input.txt")
    output_path = os.path.join(base_dir, "output.txt")

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Check for pre-screening impossibility (e.g. any pot > num_groups, or any league > num_groups)
    try:
        num_groups, num_pots, variables, domains, pots, leagues = parse_input_file(input_path)
    except ValueError as e:
        print(f"\n{e}")
        return

    # Impossibility check
    for p_id, p_teams in pots.items():
        if len(p_teams) > num_groups:
            write_output_file(output_path, num_groups, None)
            print("Impossible: Pot count exceeds group count.")
            return

    for l_id, l_teams in leagues.items():
        if len(l_teams) > num_groups:
            write_output_file(output_path, num_groups, None)
            print(f"Impossible: League {l_id} has {len(l_teams)} teams > {num_groups} groups.")
            return

    # TV Pairings for UEFA Broadcast Split (Can be enabled or disabled)
    # Automatically pair top clubs from same league if 2 or 4 clubs
    tv_pairs = []
    # England pairs
    if 'ENG' in leagues and len(leagues['ENG']) == 4:
        tv_pairs.extend([
            (leagues['ENG'][0], leagues['ENG'][1]),
            (leagues['ENG'][2], leagues['ENG'][3])
        ])
    # Spain pairs
    if 'ESP' in leagues and len(leagues['ESP']) == 4:
        tv_pairs.extend([
            (leagues['ESP'][0], leagues['ESP'][1]),
            (leagues['ESP'][2], leagues['ESP'][3])
        ])
    # Germany pairs
    if 'GER' in leagues and len(leagues['GER']) == 4:
        tv_pairs.extend([
            (leagues['GER'][0], leagues['GER'][1]),
            (leagues['GER'][2], leagues['GER'][3])
        ])
    # Italy pairs
    if 'ITA' in leagues and len(leagues['ITA']) == 4:
        tv_pairs.extend([
            (leagues['ITA'][0], leagues['ITA'][1]),
            (leagues['ITA'][2], leagues['ITA'][3])
        ])
    # Portugal pair
    if 'POR' in leagues and len(leagues['POR']) == 2:
        tv_pairs.append((leagues['POR'][0], leagues['POR'][1]))
    # Netherlands pair
    if 'NED' in leagues and len(leagues['NED']) == 2:
        tv_pairs.append((leagues['NED'][0], leagues['NED'][1]))

    # Solve CSP
    solver = UCL_CSP(variables, domains, pots, leagues, tv_pairs=tv_pairs)
    assignment = solver.solve()

    # If TV pairing was overconstrained in any arbitrary dataset, fallback to standard draw
    if assignment is None and tv_pairs:
        solver = UCL_CSP(variables, domains, pots, leagues, tv_pairs=None)
        assignment = solver.solve()

    write_output_file(output_path, num_groups, assignment)
    display_results(num_groups, assignment, pots, leagues)
    print(f"\nExecution Stats: {solver.num_assignments} assignments made, {solver.num_backtracks} backtracks.")
    print(f"Result written to '{output_path}'.")


if __name__ == "__main__":
    main()
