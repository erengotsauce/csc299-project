from openai import OpenAI

def main() -> None:
    client = OpenAI()

    # system prompt
    system_prompt = {"role": "system", "content": "You are a helpful assistant, which will summarize paragraph-length descriptions into a single concisesentence."}

    # initial queries provided up front (processed one-by-one)
    initial_queries = [
        {"role": "user", "content": "The gas giant was a swirling marble of impossible colors, a colossal sentinel silently orbiting a distant, dying star. Its atmosphere was a chaotic tapestry woven from hydrogen and helium, striated with bands of ruby-red storms that had been raging for millennia and faint, emerald-green aurorae flickering at the poles. High above the churning clouds, strange, bioluminescent plankton-like organisms, no larger than a human thumbnail, drifted in immense, slow-moving shoals, catching the weak, scattered light and turning the deep violet of space into a shimmering, living haze. The planet's gravity was a crushing, relentless force, yet it was this very force that sculpted the sublime, terrifying beauty of its surface, eternally pulling the cosmic dust and light into its grand, silent, and endless dance."},
        {"role": "user", "content": "The air in the back aisle was thick and heavy, a complex, comforting perfume unique to aging paper and forgotten leather. It was a smell that transcended mere dust; it carried notes of dry vanilla, a ghost of pipe tobacco from a long-retired proprietor, and the subtle, earthy sweetness of decaying glue binding spines that hadn't been opened in decades. Sunlight, fragmented and hazy, slanted through a high, dusty window, illuminating millions of motes suspended in the stillness, turning the space into a luminous, golden cavern. This particular nook, dedicated to forgotten maritime histories and obscure Latin translations, felt less like a retail space and more like a carefully preserved time capsule, promising a quiet, uninterrupted journey into worlds that existed only between the brittle, sepia-toned pages."}
    ]

    # user query
    print("Processing queries...")

    for q in initial_queries:
        queryNumber = initial_queries.index(q) + 1
        messages = [system_prompt, q]
        # get response from model
        completion = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[system_prompt, q]
        )

        # print model response
        print(f"\nQuery {queryNumber}: {completion.choices[0].message.content}")
