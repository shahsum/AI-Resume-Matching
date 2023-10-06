def print_pipeline(doc):
    tokens = []
    for token in doc:
        tokens.append(token.text)
    print("=================== step 1: tokenization =========================")
    print(tokens)
    print("")

    tags = []
    for token in doc:
        tags.append(f"Token: {token.text}, POS Tag: {token.pos_}")
    print("=================== step 2: part-of-speech tagging =========================")
    print(tags)
    print("")

    deps = []
    for token in doc:
        deps.append(f"Token: {token.text}, Dependency Label: {token.dep_}")
    print("=================== step 3: Parsing Dependency Labels =========================")
    print(deps)
    print("")

    lemmas = []
    for ent in doc:
        lemmas.append(f"Token: {ent.text}, Lemma: {ent.lemma_}")
    print("=================== step 4: lemmatizing =========================")
    print(lemmas)
    print("")

    labels = []
    for ent in doc.ents:
        labels.append(f"Token: {ent.text}, Label: {ent.label_}")
    print("=================== step 5: custom named entity recognition =========================")
    print(labels)
    print("")

    stops = []
    for ent in doc:
        if ent.is_stop:
            stops.append(ent.text)
    print("=================== step 6: stop words removal =========================")
    print(stops)
    print("")