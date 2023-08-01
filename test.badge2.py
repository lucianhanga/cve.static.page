from jinja2 import Environment, FileSystemLoader

# Set up the Jinja2 environment and load the template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('./templates/badge2.jinja2')

# Render the template with the software version
rendered_template = template.render(part1="Jira", part2="8.19", part3="HIGH")

# print(rendered_template)
# render in a file
with open('badge1.html', 'w') as f:
    f.write(rendered_template)
