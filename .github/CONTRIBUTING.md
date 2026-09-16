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
  - name: Window Management
    repos:
      - url: https://github.com/owner/window-manager
        description: "Tiling window manager for macOS"

  - name: Browsers
    repos:
      - url: https://github.com/owner/browser

  - name: Audio & Video
    subcategories:
      - name: Players
        repos:
          - url: https://github.com/owner/player
      - name: Editors
        repos:
          - url: https://github.com/owner/editor
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