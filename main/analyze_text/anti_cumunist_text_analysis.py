import docx
import re
from PyPDF2 import PdfReader
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx



from words.key_words import communism_key_words as key_words
from words.negative_words import negative_words as negative_words
from words.connectors_articles import connectors_articles as connectors_articles


path_file = "../../resourses/prueba.txt"

connectors_articles_set = connectors_articles
key_words_set = key_words
negative_words_set = negative_words


def determine_document_type(path_file):
    try:
        if path_file.endswith('.pdf'):
            with open(path_file, 'rb') as f:
                reader = PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + ' '
                return text

        elif path_file.endswith('.docx'):
            doc = docx.Document(path_file)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + ' '

            return text

        elif path_file.endswith('.txt'):
            with open(path_file, 'r', encoding='utf-8') as f:
                text = f.read()

            return text

        else:

            print(f"El tipo de archivo '{path_file}' no es compatible.")

            return None

    except FileNotFoundError:

        print(f"El archivo '{path_file}' no se encontró.")

        return None

    except Exception as e:

        print(f"Se produjo un error al leer el archivo '{path_file}': {str(e)}")

        return None

def normalize_text(text):
    # Convertir el texto a minúsculas
    text = text.lower()

    # Eliminar espacios dobles
    text = re.sub(r'\s+', ' ', text)

    # Eliminar caracteres especiales excepto guiones dentro de palabras
    text = re.sub(r'[^\w\s]', '', text)

    normalized_text = text.split()

    # Filtrar las palabras que no estén en el conjunto de conectores y artículos
    filtered_words = [word for word in normalized_text if word not in connectors_articles_set]

    return filtered_words

def count_words(words):

    # Contar el número total de palabras
    total_word_count = len(words)

    # Contar palabras únicas
    unique_word_count = len(set(words))

    return total_word_count, unique_word_count

def show_count_per_word(words):
    word_count = {}
    # Muestra la cantidad que existe de cada palabra
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    for word, count in word_count.items():
        print(f"{word}: {count}")
    return word_count

def show_count_per_key_words(words):
    word_count = {}
    # Muestra la cantidad que existe de cada palabra clave
    for word in words :
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    for word, count in word_count.items():
        if word in key_words_set:
            print(f"{word}: {count}")

def show_count_per_negative_words(words):
    word_count = {}
    # Muestra la cantidad que existe de palabras negativas
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    for word, count in word_count.items():
        if word in negative_words_set:
            print(f"{word}: {count}")

def show_word_frequency(words):
    word_freq = Counter(words)
    total_words = count_words(words)[0]

    # Mostrar la frecuencia de cada palabra como porcentaje y ocurrecia
    for word, freq in word_freq.items():
        if freq == 1:
            print(f"{word}, Frecuencia: Única")
        else:
            freq_percentage = (freq / total_words) * 100
            print(f"{word}, Frecuencia: {freq_percentage:.2f}%, Se repite cada {100/freq_percentage:.2f} palabras")

def calculate_score(text, key_words, negative_words):
    score = 0
    words = text

    # Diccionarios para almacenar los puntajes de las palabras clave y las palabras que contribuyen
    dictionary_words = {}
    key_word_scores = {}
    contributing_scores = {}
    contributing_words = {}


    for i in range(len(words)):
        word = words[i]
        if word in key_words:

            if word in dictionary_words:
                contributing_words = dictionary_words[word]
            else:
                contributing_words = {}

            dictionary_words[word] = contributing_words


            # Buscar hasta 2 palabras hacia atrás
            for j in range(i - 1, max(-1, i - 3), -1):

                if words[j] in negative_words:
                    count_negative_word = 0
                    negative_word = words[j]

                    if negative_word in contributing_words:
                        count_negative_word = contributing_words[negative_word]
                        count_negative_word += 1
                    else:
                        count_negative_word = 1

                    contributing_words[negative_word] = count_negative_word



            # Buscar hasta 2 palabras hacia adelante
            for k in range(i + 1, min(len(words), i + 3)):
                if words[k] in negative_words:
                    count_negative_word = 0
                    negative_word = words[k]
                    if negative_word in contributing_words:
                        count_negative_word = contributing_words[negative_word]
                        count_negative_word += 1
                    else:
                        count_negative_word = 1
                    contributing_words[negative_word] = count_negative_word


            dictionary_words[word] = contributing_words

    for word in dictionary_words:
        for negative_word in dictionary_words[word]:
            score += key_words[word] * negative_words[negative_word] * dictionary_words[word][negative_word]

    print("Puntaje global:", score)
    for word, score in key_word_scores.items():
        print(f"Palabra clave: {word} (puntaje {score}), Palabras que contribuyen: ", end= " ")
        for word, score in contributing_scores.items():
            print(f"{word} (puntaje {score})", end=" ")
        print()
    return score, dictionary_words

def all_word_cloud_graph(words):
    if not words:
        return
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(words)
    # Mostrar la nube de todas las palabras
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def key_word_cloud_graph(words):
    key_words = {}
    for i in words:
        if i in key_words_set:
            key_words[i] = key_words.get(i, 0) + 1
    if not key_words:
        return
    wordcloud2 = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(key_words)

    # Mostrar la nube de las palabras clave
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud2, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def negative_word_cloud_graph(words):

    negative_words = {}
    for i in words:
        if i in negative_words_set:
            negative_words[i] = negative_words.get(i, 0) + 1
    if not negative_words:
        return
    wordcloud3 = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(negative_words)

    # Mostrar la nube de las palabras negativas
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud3, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def word_bar_chart(words):
    if not words:
        return
    sorted_words = sorted(words.items(), key=lambda x: x[1], reverse=True)

    # Tomar las 20 primeras palabras con los valores más altos
    top_20_words = sorted_words[:20]

    top_words, frequencies = zip(*top_20_words)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    plt.bar(top_words, frequencies, color='skyblue')
    plt.xlabel('Palabra clave')
    plt.ylabel('Frecuencia')
    plt.title('Top Palabras')
    plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mayor legibilidad
    plt.tight_layout()
    plt.show()

def key_word_bar_chart(words):
    key_words = {}
    for word, value in words.items():
        if word in key_words_set:
            key_words[word] = value
    if not key_words:
        return
    sorted_key_words = sorted(key_words.items(), key=lambda x: x[1], reverse=True)

    # Tomar las 20 primeras palabras clave con los valores más altos
    top_20_key_words = sorted_key_words[:20]

    top_key_words, frequencies = zip(*top_20_key_words)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    plt.bar(top_key_words, frequencies, color='skyblue')
    plt.xlabel('Palabra clave')
    plt.ylabel('Frecuencia')
    plt.title('Top Palabras Clave')
    plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mayor legibilidad
    plt.tight_layout()
    plt.show()

def negative_word_bar_chart(words):
    negative_words = {}
    for word, value in words.items():
        if word in negative_words_set:
            negative_words[word] = value
    if not negative_words:
        return

    sorted_negative_words = sorted(negative_words.items(), key=lambda x: x[1], reverse=True)

    # Tomar las 20 primeras palabras negativas con los valores más altos
    top_20_negative_words = sorted_negative_words[:20]

    top_negative_words, frequencies = zip(*top_20_negative_words)

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    plt.bar(top_negative_words, frequencies, color='skyblue')
    plt.xlabel('Palabra clave')
    plt.ylabel('Frecuencia')
    plt.title('Top Palabras Negativas')
    plt.xticks(rotation=45, ha='right')  # Rotar las etiquetas del eje x para mayor legibilidad
    plt.tight_layout()
    plt.show()

def plot_word_connections(dictionary_words):
    G = nx.Graph()
    for word in dictionary_words:

        for negative_word in dictionary_words[word]:
            negative_score = negative_words_set[negative_word]

            G.add_edge(word, negative_word, weight=negative_score)

    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Conexiones de palabras")
    plt.show()


def plot_word_connections_value(dictionary_words):

    G = nx.Graph()
    for word in dictionary_words:

        for negative_word in dictionary_words[word]:
            negative_score = negative_words_set[negative_word] * key_words_set[word] * dictionary_words[word][negative_word]
            G.add_edge(word, negative_word, weight=negative_score)

    pos = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Conexiones de palabras")
    plt.show()

def classify_anticommunism(score, count):
    if score == 0:
        return "No anticomunista"
    scale = count / score
    if scale <= 5:
        return "Muy anticomunista"
    elif scale <= 6.25:
        return "Anticomunista"
    elif scale <= 8.3:
        return "Considerablemente anticomunista"
    elif scale <= 6.25:
        return "Poco anticomunista"
    elif scale <= 12.5:
        return "Muy poco anticomunista"
    else:
        return "No anticomunista"


def run():

    text = normalize_text(determine_document_type(path_file))
    print("Texto normalizado", text)
    total_words = count_words(text)[0]
    print("El numero de palabras dentro del texto es:", count_words(text)[0])
    print("El numero de palabras únicas del texto es:", count_words(text)[1])

    print()
    print("Conteo por palabra")
    count = show_count_per_word(text)

    print()
    print("Frecuencia de las palabras")
    show_word_frequency(text)


    print()
    print("Conteo de palabras clave")
    show_count_per_key_words(text)

    print()
    print("Conteo de palabras negativas")
    show_count_per_negative_words(text)

    print()
    print("Score del texto")
    score, dictionary_word = calculate_score(text, key_words_set, negative_words_set)


    print()
    print("Clasificación del texto")
    print(classify_anticommunism(score, total_words))

    all_word_cloud_graph(count)
    key_word_cloud_graph(count)
    negative_word_cloud_graph(count)
    word_bar_chart(count)
    key_word_bar_chart(count)
    negative_word_bar_chart(count)
    plot_word_connections(dictionary_word)
    plot_word_connections_value(dictionary_word)

run()


