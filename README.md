# Vestige

Vestige is a tool that automatically finds and removes commented code from python files.

For example, you can use the tool to remove some comments within it's main file, and output the result into another file cleaned.py like this.
```
python -m vestige --input cleaner.py --output cleaned.py
```

## Q/A
- Will vestige break my code!?

Thankfully, no! Vestige only analyzes inline comments, so while it's possible for it to remove some inline documentation by mistake, it won't ever affect the actual code.
- How much can I trust vestige?

Vestige's current model is about 95% accurate on internal tests- we recommend double checking the diff of the original and output final to ensure everything has worked properly.  In the future we are aiming to increase this accuracy significantly through improvement of both the model and the training dataset.

- How does vestige work?

Vestige uses [BERT](https://arxiv.org/abs/1810.04805), a transformer based artificial neural network that is pretrained to better *understand (kind of)* language, and then fine tuned on a specific task.  In this case, it is fine tuned to distinguish between commented code and useful documentation.
