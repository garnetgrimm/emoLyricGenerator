import os
import markovify

combined_model = None
for (dirpath, _, filenames) in os.walk("lyrics"):
    for filename in filenames: 
        #print(filename)
        with open(os.path.join(dirpath, filename)) as f:
            model = markovify.Text(f, retain_original=False)
            if combined_model:
                combined_model = markovify.combine(models=[combined_model, model])
            else:
                combined_model = model

# Print three randomly-generated sentences of no more than 280 characters
for i in range(15):
    print(combined_model.make_sentence())
