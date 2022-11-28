import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def num_genes(person, one_gene, two_genes):
    """
    Calculate number of genes to test for.
    """
    if person in one_gene:
        assert person not in two_genes
        return 1
    elif person in two_genes:
        return 2
    else:
        return 0


def prob_inheritance(condition):
    """
    Calculate probablity for inheritance with or without mutation.
    """
    return 1 - PROBS["mutation"] if condition else PROBS["mutation"] 


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    prob = 1  # Idempotent for multiplication
    for person in people.keys():
        num_genes_person = num_genes(person, one_gene, two_genes)
        # Calculate probability to have n copies of the gene:
        # For a person with no parents in the dataset, use data from PROBS
        if people[person]["mother"] is None or people[person]["father"] is None:
            prob *= PROBS["gene"][num_genes_person] 
        # Else get data from parents * mutation
        else:
            num_genes_mother = num_genes(people[person]["mother"], one_gene, two_genes)
            num_genes_father = num_genes(people[person]["father"], one_gene, two_genes)
            if num_genes_person == 1:
                if num_genes_mother == 1 or num_genes_father == 1:
                    # 1 gene for person and 1 gene for at least one parent
                    prob *= 0.5 * prob_inheritance(True) + 0.5 * prob_inheritance(False)
                elif num_genes_mother == num_genes_father:
                    # 1 gene for person, 0 or 2 genes for both mother and father
                    prob *= prob_inheritance(True) * prob_inheritance(False) * 2
                else:
                    # 1 gene for person, 0 genes for mother and 2 for father or vice versa
                    prob *= prob_inheritance(True) ** 2 + prob_inheritance(False) ** 2
            else:
                if num_genes_mother == 1 or num_genes_father == 1:
                    # 0 or 2 genes for person and 1 gene for at least one parent
                    prob *= 0.5 * prob_inheritance(True) + 0.5 * prob_inheritance(False)
                    if num_genes_mother == 1 and num_genes_father == 1:
                        # 0 or 2 genes for person and 1 gene for both parents
                        prob *= 0.5 * prob_inheritance(True) + 0.5 * prob_inheritance(False)
                    else:
                        # 0 or 2 genes for person and one parent, 1 gene for the other parent
                        prob *= prob_inheritance(num_genes_mother == num_genes_person or num_genes_father == num_genes_person)
                else:
                    # 0 or 2 genes for person and both parents
                    prob *= (prob_inheritance(num_genes_mother == num_genes_person) *
                             prob_inheritance(num_genes_father == num_genes_person))

        # Calculate probability to have the trait according to number of genes for person
        prob *= PROBS["trait"][num_genes_person][person in have_trait]

    return prob

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities.keys():
        probabilities[person]["gene"][num_genes(person, one_gene, two_genes)] += p
        probabilities[person]["trait"][person in have_trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities.keys():
        gene_factor = 1 / sum(probabilities[person]["gene"].values())
        trait_factor = 1 / sum(probabilities[person]["trait"].values())
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] *= gene_factor
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] *= trait_factor


if __name__ == "__main__":
    main()
