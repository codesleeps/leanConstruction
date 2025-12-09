# Contributing to Lean Construction AI

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Docker version, etc.)
   - Logs or screenshots if applicable

### Suggesting Features

1. Check existing issues and discussions
2. Create a feature request with:
   - Clear use case
   - Expected behavior
   - Potential implementation approach
   - Impact on existing features

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Update documentation
6. Submit a pull request

## 🔧 Development Setup

### Prerequisites

- Docker Desktop
- Node.js 18+
- Python 3.11+
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/lean-construction-ai.git
cd lean-construction-ai

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/lean-construction-ai.git

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
cd ../mobile && npm install
```

### Running Locally

```bash
# Start all services
docker-compose up -d

# Or run individually
cd backend && uvicorn app.main:app --reload
cd frontend && npm start
cd mobile && npm run ios  # or android
```

## 📝 Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Maximum line length: 100 characters

```python
def calculate_waste_impact(
    waste_type: str,
    cost: float,
    time: float
) -> Dict[str, Any]:
    """
    Calculate the impact of waste on project metrics.
    
    Args:
        waste_type: Type of waste (DOWNTIME)
        cost: Financial impact in dollars
        time: Time impact in hours
    
    Returns:
        Dictionary with impact analysis
    """
    pass
```

### JavaScript/React (Frontend & Mobile)

- Use ES6+ features
- Follow Airbnb style guide
- Use functional components with hooks
- PropTypes or TypeScript for type checking

```javascript
const WasteCard = ({ waste, onPress }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <Card onPress={onPress}>
      <Text>{waste.type}</Text>
    </Card>
  );
};
```

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(backend): add waste prediction model
fix(mobile): resolve login token refresh issue
docs(readme): update deployment instructions
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Mobile Tests

```bash
cd mobile
npm test
```

### Integration Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📋 Pull Request Process

1. **Update your fork**
```bash
git fetch upstream
git rebase upstream/main
```

2. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make changes**
- Write clean, documented code
- Add/update tests
- Update documentation

4. **Test thoroughly**
```bash
# Run all tests
pytest
npm test
docker-compose up -d  # Verify services work
```

5. **Commit changes**
```bash
git add .
git commit -m "feat(scope): description"
```

6. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

7. **Create Pull Request**
- Clear title and description
- Reference related issues
- Include screenshots if UI changes
- Ensure CI passes

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] CI/CD passes
- [ ] Reviewed by maintainer

## 🏗️ Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

Key directories:
- `backend/app/` - FastAPI application
- `frontend/src/` - React components
- `mobile/src/` - React Native screens
- `backend/tests/` - Backend tests
- `.github/workflows/` - CI/CD

## 🔍 Code Review Process

1. Maintainer reviews PR
2. Feedback provided via comments
3. Author addresses feedback
4. Maintainer approves
5. PR merged to main

### Review Criteria

- Code quality and readability
- Test coverage
- Documentation completeness
- Performance impact
- Security considerations
- Breaking changes

## 🐛 Debugging

### Backend Issues

```bash
# View logs
docker-compose logs -f backend

# Access container
docker exec -it <container-id> bash

# Run Python shell
docker exec -it <container-id> python
```

### Frontend Issues

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check console
# Open browser DevTools
```

### Database Issues

```bash
# Access database
docker exec -it <postgres-container> psql -U postgres -d leandb

# View tables
\dt

# Query data
SELECT * FROM users;
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Documentation](https://docs.docker.com/)

## 🎯 Areas for Contribution

### High Priority

- [ ] Computer vision models (Phase 2)
- [ ] Waste detection algorithms
- [ ] Predictive analytics models
- [ ] Additional PM tool integrations
- [ ] Mobile app camera functionality
- [ ] Real-time notifications

### Medium Priority

- [ ] Advanced analytics dashboards
- [ ] Report generation (PDF)
- [ ] Email notifications
- [ ] User management UI
- [ ] Project templates
- [ ] Data export features

### Low Priority

- [ ] UI/UX improvements
- [ ] Performance optimizations
- [ ] Additional tests
- [ ] Documentation improvements
- [ ] Code refactoring
- [ ] Accessibility features

## 💬 Communication

- **GitHub Issues**: Bug reports and features
- **Pull Requests**: Code contributions
- **Discussions**: General questions and ideas

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## ❓ Questions?

- Check existing documentation
- Search closed issues
- Create a new discussion
- Contact maintainers

## 🎉 Thank You!

Every contribution helps make this project better. We appreciate your time and effort!

---

**Happy Coding!** 🚀
