# Contributing Guidelines

Thank you for your interest in contributing to this awesome list! 🎉

## How to Contribute

**Important:** This README is automatically generated from `repositories.yaml`. Please **DO NOT** edit the README.md directly. Instead, make your changes to the `repositories.yaml` file.

### Adding Repositories

1. **Fork** this repository
2. **Edit** the `repositories.yaml` file
3. **Add** your repository to the appropriate category
4. **Submit** a pull request

## File Structure

All contributions should be made to the `repositories.yaml` file using the following structure:

### Basic Repository Entry

```yaml
categories:
  - name: Category Name
    repos:
      - url: https://github.com/owner/repository-name
```

### Repository with Description (Optional)

```yaml
categories:
  - name: Category Name
    repos:
      - url: https://github.com/owner/repository-name
        description: "Brief description of what this repository does"
```

### Category with Description

```yaml
categories:
  - name: Category Name
    description: "Brief description of this category"
    repos:
      - url: https://github.com/owner/repository-name
```

### Subcategories

```yaml
categories:
  - name: Main Category
    subcategories:
      - name: Subcategory Name
        repos:
          - url: https://github.com/owner/repository-name
          - url: https://github.com/owner/another-repository
```

## Complete Example

Here's a complete example showing different structures:

```yaml
categories:
  - name: Agents
    description: "AI agents and autonomous systems"
    repos:
      - url: https://github.com/smol-ai/developer
      - url: https://github.com/Aider-AI/aider
        description: "AI pair programming in your terminal"
      - url: https://github.com/AntonOsika/gpt-engineer
      - url: https://github.com/joshpxyne/gpt-migrate

  - name: App generators
    repos:
      - url: https://github.com/stackblitz-labs/bolt.diy
        description: "Prompt, run, edit, and deploy full-stack web applications"
      - url: https://github.com/srcbookdev/srcbook

  - name: Assistants
    subcategories:
      - name: Command-line
        repos:
          - url: https://github.com/Strawberry-Computer/poorcoder
          - url: https://github.com/BrodaNoel/cmd-ai
      - name: IDE extensions
        repos:
          - url: https://github.com/smallcloudai/refact
          - url: https://github.com/codota/TabNine
          - url: https://github.com/rubberduck-ai/rubberduck-vscode
      - name: Web-based
        repos:
          - url: https://github.com/silvanmelchior/IncognitoPilot

  - name: Documentation
    repos:
      - url: https://github.com/eli64s/readme-ai
        description: "Beautiful README files from the command line"
```

## Guidelines

### Repository Requirements

- **GitHub only**: Only GitHub repositories are accepted
- **Active projects**: Repository should be actively maintained
- **Quality**: High-quality, useful projects
- **Relevant**: Must fit the theme of the awesome list

### Quality Standards

- Repository should have a clear README
- Should be open source
- Must have meaningful commit history
- Should provide value to the community

### Categories

- Use existing categories when possible
- Create new categories only when necessary
- Keep category names clear and descriptive
- Use subcategories for better organization when needed

### Descriptions (Optional)

- Keep descriptions brief and informative
- Focus on what the repository does, not marketing language
- Use sentence case
- End with a period if it's a complete sentence

## What Happens Next?

1. Your pull request will be reviewed
2. If approved, the changes will be merged
3. The README.md will be automatically regenerated
4. Your contribution will appear in the updated list

---

**Note**: The README.md file is automatically generated. Any manual edits to README.md will be overwritten during the next update.