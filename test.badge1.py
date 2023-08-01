from jinja2 import Environment, FileSystemLoader

# Set up the Jinja2 environment and load the template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('./templates/badge1.jinja2')

# Render the template with the software version
rendered_template = template.render(version='1.2.3')

# print(rendered_template)
# render in a file
with open('badge1.html', 'w') as f:
    f.write(rendered_template)
