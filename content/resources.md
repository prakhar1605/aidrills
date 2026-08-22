Things worth reading before an AI engineering interview. Short list on purpose —
everything here is either the primary source or the clearest explanation of
something a drill on this site asks you to implement.

Links rot. Open a PR if one has.

## Foundations

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — the paper. Section 3.2.1 is the one the interview is about.
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — Jay Alammar. Read this before the paper if the paper does not land.
- [minbpe](https://github.com/karpathy/minbpe) — Karpathy's minimal BPE, with the accompanying "Let's build the GPT Tokenizer" video.
- [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) — Harvard NLP. The paper as runnable code.

## Retrieval

- [Practical BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-variables) — Elastic. The clearest explanation of `k1` and `b` anywhere.
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) — Cormack et al., SIGIR 2009. Four pages, one formula.
- [Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2312.10997) — a map of the space, useful for the design round.

## Plumbing

- [Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) — AWS Architecture Blog. Read it once and you will never write fixed backoff again.
- [Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html) — the WHATWG spec. Shorter than you expect.
- [OpenAI Cookbook](https://cookbook.openai.com/) — practical recipes; the retry and streaming ones map directly onto drills here.

## Agents

- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) — Anthropic. The taxonomy interviewers use when they ask "would you use an agent here?".
- [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) — Lilian Weng. The reference survey.

## Evals & safety

- [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) — where exact match and token F1 come from.
- [Prompt injection](https://simonwillison.net/tags/prompt-injection/) — Simon Willison has tracked this from the start; the tag is the best archive there is.
- [Chip Huyen's blog](https://huyenchip.com/blog/) — evals, LLM systems, and what breaks in production.

## The runtime under this site

- [Pyodide](https://pyodide.org/) — CPython compiled to WebAssembly. It is what runs your code in the tab, with no server involved.
