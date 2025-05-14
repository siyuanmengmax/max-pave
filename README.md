# Max-Pave: Pavement Management System

![License](https://img.shields.io/badge/license-MIT-blue.svg)

Max-Pave is a comprehensive Django-based pavement management system that combines traditional infrastructure management with computer vision for automated road condition assessment. This system helps municipalities, transportation departments, and contractors efficiently manage road infrastructure maintenance planning.

## Features

- **Road Inventory Management**: Track road sections with detailed information
- **Computer Vision Analysis**: Automatically detect and quantify pavement cracks from images
- **Condition Assessment Tracking**: Monitor pavement condition indices (PCI) over time
- **Maintenance Planning**: Schedule and track maintenance activities
- **Dashboard Visualization**: View key metrics and statistics at a glance
- **User Authentication**: Secure access to system features

## Technology Stack

- **Backend**: Django 5.1
- **Frontend**: Bootstrap 5
- **Database**: SQLite (default), compatible with PostgreSQL
- **Computer Vision**: OpenCV
- **Data Visualization**: Bootstrap components

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/max-pave.git
   cd max-pave
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database
   ```bash
   # Generate migration files based on model changes
   python manage.py makemigrations
   
   # Apply migrations to the database
   python manage.py migrate
    ```

5. Load sample data (optional)
   ```bash
   python manage.py load_sample_data
   ```

6. Create media directories for image storage
   ```bash
   mkdir -p media/pavement_images
   mkdir -p media/analysis_results
   ```

7. Start the development server
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

## Usage

1. **Login**: Use the default admin account (username: "admin", password: "admin") or create a new account
2. **Road Inventory**: Add and manage road sections in your infrastructure
3. **Condition Assessment**: Upload pavement images for automated crack detection and PCI calculation
4. **Maintenance Planning**: Schedule maintenance activities based on condition assessments
5. **Dashboard**: Monitor your pavement network's health and upcoming activities

## System Architecture

The system consists of several Django apps with specific responsibilities:

- **core**: Central dashboard and shared functionality
- **inventory**: Road section management
- **assessments**: Condition assessment and image analysis
- **maintenance**: Maintenance planning and tracking
- **reports**: Reporting functionality

## Future Enhancements

- Advanced crack classification (longitudinal, transverse, alligator)
- Machine learning models for more accurate deterioration prediction
- Mobile app integration for field inspections
- GIS integration for map-based visualization
- Advanced reporting and analytics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed by Siyuan Max Meng
- Inspired by the need for efficient infrastructure management
- Built on open-source technologies