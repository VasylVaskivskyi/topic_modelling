import re
from nltk.stem import WordNetLemmatizer
#r'\+':'\\+' , \[\]\{\}
def sci_term_replacer(data:str) -> str: #replace scietific terms and some symbols, uderscores can be used to preserve order
    data_str = data
    replace_dict = { "’":"'", "'s":"", '-(\d+)-': r'_\1_', '[-—=/\'\"\*\$\^]':' ','\sas\s':' as_', '(\.org|\.com)':'', '[^\w][a-z]\.\s?':';', r'\bvs\b':'versus',
                    'europe pmc':'europepmc', r'[\s-]prot\b':'prot',
                    'sp\.':'species','spp\.':'species',
                    'variations':'variation', 'cnv[s]?': 'copy number variation', 'copy number change[s]?':'copy number variation',
                    'polymorphisms':'polymorphism','snp[s]?': 'single nucleotide polymorphism',
                    'snv[s]': 'single nucleotide variation', 'single nucleotide varia(tions|nts|nt)':'single nucleotide variation',
                    'genes':'gene','proteins':'protein','peptides':'peptide',
                    'deletions':'deletion','microdeletions':'microdeletion','loci':'locus','markers':'marker','breakpoints':'breakpoint',
                    'duplications':'duplication','mutation(al|s)':'mutation',
                    'abnormally':'abnormality','absence':'absent','disorders':'disorder','neoplasms':'neoplasm',
                    'cardiac':'heart','age(d|ing)':'age','genomic':'genome','meiotic':'meiosis','mitotic':'mitosis',
                    'humans':'human','mice':'mouse','chickens':'chicken','chick':'chicken','rats':'rat','cells':'cell','bacterial':'bacteria','fungal':'fungi','viral':'virus',
                    'cultured': 'culture','cultural':'culture',
                    'contigs':'contig', 'mir':'micro rna','micrornas':'micro rna',r'\brnas\b':'rna','amino acid':'amino_acid','nucleic acid':'nucleic_acid',
                    'publically':'public','forecast':'prognosis','forecasting':'prognosis','vaccination':'vaccine',
                    r'\bil\b':'interleukin',
                    'type (1|2) diabetes mellitus':r'diabetes mellitus type \1', 'type (1|2) diabetes':r'diabetes mellitus type \1',
                    'united states':'united_states','u\.s\.':'united_states',
                    'de novo': 'de_novo', 'ad hoc': 'ad_hoc', 'in situ': 'in_situ', 'in vivo': 'in_vivo', 'in vitro': 'in_vitro', 'ex vivo': 'ex_vivo',
                    r'\balpha\b': 'α', r'\bbeta\b': 'β', r'\bgamma\b': 'γ', r'\bdelta\b': 'δ', r'\bepsilon\b': 'ε', r'\bzeta\b': 'ζ', r'\beta\b': 'η',
                    r'\btheta\b': 'θ', r'\biota\b': 'ι', r'\bkappa\b': 'κ', r'\blambda\b': 'λ', r'\bmu\b': 'μ', r'\bnu\b': 'ν', r'\bxi\b': 'ξ',
                    r'\bomicron\b': 'ο',r'\bpi\b': 'π', r'\brho\b': 'ρ', r'\bsigma\b': 'σ', r'\btau\b': 'τ', r'\bupsilon\b': 'υ', r'\bphi\b': 'φ', r'\bchi\b': 'χ',
                    r'\bpsi\b': 'ψ',r'\bomega\b': 'ω'
                    }

    for key in replace_dict:
        data_str = re.sub(key, replace_dict[key], data_str)
    return data_str


lemmatizer = WordNetLemmatizer()

#sets are faster for checking if object is in it
stop_words_set = {'', 'a', 'about', 'an', 'and', 'are', 'at', 'as', 'be', 'by', 'but', 'for', 'from', 'how',
                    'in', 'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when',
                    'where', 'with','which','+',
                    'http', 'https','internet','software',
                    'science','university','disease',
                    'human','mouse','rat','animal','plant','cell','bacteria','virus','fungi',
                    'age', 'no.',
                    'protein', 'peptide', 'enzyme',
                    'male', 'female'} #,'child', 'infant', 'newborn', 'young','adult', 'preschool','adolescent', 'youth']
