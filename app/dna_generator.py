# Simulated expensive DNA generator
def generate_dna_sequence(id, region, age, seed):
    import hashlib
    import random

    base = f"{id}:{region}:{age}:{seed}"
    hash_value = hashlib.sha256(base.encode()).hexdigest()
    random.seed(int(hash_value[:8], 16))
    return ''.join(random.choices("ATCG", k=200))
