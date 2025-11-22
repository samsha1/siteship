# routes/webhook.py
from fastapi import APIRouter, Request, logger, status, Form
from fastapi.responses import JSONResponse
from src.handlers.whatsapp import send_message
from src.handlers.supabase import save_html_to_storage, trigger_edge_function_and_deploy_to_vercel
from src.utils.parser import parse_mode_response_code, cleanup_temp_dir
from src.common.logger import get_logger
from src.services.db import (
    get_user_by_phone, create_user, update_user_state, create_project,
    get_user_projects, get_project_by_id, save_prompt
)
import json

logger = get_logger(__name__)

router = APIRouter()


@router.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request, From: str = Form(...), To: str = Form(...), Body: str = Form(...)):
    """Handle incoming WhatsApp webhook requests."""
    logger.info(f"From: {From}, To: {To}, Body: {Body}")
    
    # Get clients from app.state
    supabase = request.app.state.supabase
    twilio = request.app.state.twilio
    
    form_data = await request.form()
    data = dict(form_data)
    message_id = data.get('SmsMessageSid')
    wa_id = data.get('WaId')
    profile_name = data.get('ProfileName')

    if not message_id or not wa_id or not Body:
        return {"ok": False, "reason": "Invalid payload"}

    user = await get_user_by_phone(supabase, From)

    if not user:
        # 2.1 New User
        await create_user(supabase, profile_name, From, "WA")
        send_message(twilio, To, From, "Welcome 👋\nI can help you build a website in minutes.\nLet's get started by Starting a new project. Please name your project")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    state = user.get("state")
    user_id = user["id"]

    # Handle "menu" command to reset
    if Body.strip().lower() == "menu":
        await update_user_state(supabase, user_id, "WAITING_FOR_OPTION")
        send_message(twilio, To, From, "Welcome 👋\nI can help you build a website in minutes.\nDo you want to:\n1️⃣ Start a new project\n2️⃣ Continue existing project\nReply with 1 or 2.")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    if state == "WAITING_FOR_PROJECT_NAME":
        project_name = Body.strip()
        project = await create_project(supabase, user_id, project_name)
        if project:
            await update_user_state(supabase, user_id, f"ACTIVE_PROJECT:{project['id']}")
            send_message(twilio, To, From, "Congratulations your project is created! Now, tell me more about this project so that I can help you build great websites.")
        else:
            send_message(twilio, To, From, "Failed to create project. Please try again.")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    if state == "WAITING_FOR_OPTION":
        if Body.strip() == "1":
            await update_user_state(supabase, user_id, "WAITING_FOR_PROJECT_NAME")
            send_message(twilio, To, From, "Please name your project")
        elif Body.strip() == "2":
            projects = await get_user_projects(supabase, user_id)
            if not projects:
                send_message(twilio, To, From, "You have no existing projects. Reply with 1 to start a new one.")
            else:
                msg = "Select a project to resume:\n"
                for i, p in enumerate(projects):
                    msg += f"{i+1}. {p['name']}\n"
                msg += "Reply with the number."
                await update_user_state(supabase, user_id, "WAITING_FOR_PROJECT_SELECTION")
                send_message(twilio, To, From, msg)
        else:
            send_message(twilio, To, From, "Invalid option. Reply with 1 or 2.")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    if state == "WAITING_FOR_PROJECT_SELECTION":
        try:
            selection = int(Body.strip())
            projects = await get_user_projects(supabase, user_id)
            if 1 <= selection <= len(projects):
                project = projects[selection-1]
                await update_user_state(supabase, user_id, f"ACTIVE_PROJECT:{project['id']}")
                send_message(twilio, To, From, f"Resuming project {project['name']}. Tell me what you want to change or add.")
            else:
                send_message(twilio, To, From, "Invalid selection. Please try again.")
        except ValueError:
            send_message(twilio, To, From, "Please reply with a number.")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    if state and state.startswith("ACTIVE_PROJECT:"):
        project_id = state.split(":")[1]
        project = await get_project_by_id(supabase, project_id)
        
        if not project:
             await update_user_state(supabase, user_id, "WAITING_FOR_OPTION")
             send_message(twilio, To, From, "Project not found. Returning to menu.")
             send_message(twilio, To, From, "Welcome 👋\nI can help you build a website in minutes.\nDo you want to:\n1️⃣ Start a new project\n2️⃣ Continue existing project\nReply with 1 or 2.")
             return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

        send_message(twilio, To, From, "Generating Code... This may take awhile. 🚀")
        
        await save_prompt(supabase, user_id, project_id, message_id, Body)

        last_summary = project.get("last_ai_summary", "")
        
        payload = {
            "username": wa_id,
            "project_name": project['name'],
            "prompt": Body,
            "metadata": {
                "source": "whatsapp", 
                "message_id": message_id, 
                "profile_name": profile_name,
                "project_id": project_id,
                "last_ai_summary": last_summary
            }
        }
        
        res = await trigger_edge_function_and_deploy_to_vercel(supabase, payload)
        try:
            res_json = json.loads(res)
            if res_json:
                send_message(twilio, To, From, f"Your request has been processed. Current Status: {res_json.get('status', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            send_message(twilio, To, From, "Something Went Wrong! Please Try Again.")
            
        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

    # Default for existing user with no state (or IDLE)
    await update_user_state(supabase, user_id, "WAITING_FOR_OPTION")
    send_message(twilio, To, From, "Welcome 👋\nI can help you build a website in minutes.\nDo you want to:\n1️⃣ Start a new project\n2️⃣ Continue existing project\nReply with 1 or 2.")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})


def get_static_response_to_save_gemini_call():
    """
    Returns a static response to save Gemini call.
    This is a placeholder function for future use.
    """
    return '```html\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Kathmandu Bakery</title>\n    <link rel="stylesheet" href="style.css">\n</head>\n<body>\n\n    <header>\n        <nav class="navbar">\n            <a href="#home" class="nav-logo">Kathmandu Bakery</a>\n            <ul class="nav-menu">\n                <li class="nav-item"><a href="#home" class="nav-link">Home</a></li>\n                <li class="nav-item"><a href="#about" class="nav-link">About</a></li>\n                <li class="nav-item"><a href="#menu" class="nav-link">Menu</a></li>\n                <li class="nav-item"><a href="#contact" class="nav-link">Contact Us</a></li>\n            </ul>\n            <div class="hamburger">\n                <span class="bar"></span>\n                <span class="bar"></span>\n                <span class="bar"></span>\n            </div>\n        </nav>\n    </header>\n\n    <main>\n        <section id="home" class="hero">\n            <div class="hero-content">\n                <h1>Welcome to Kathmandu Bakery</h1>\n                <p>Bringing organic from the foothills of Himalaya since 1988.</p>\n                <a href="#menu" class="cta-button">View Our Menu</a>\n            </div>\n        </section>\n\n        <section id="about" class="page-section">\n            <div class="container">\n                <h2>About Us</h2>\n                <div class="about-content">\n                    <img src="https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?q=80&w=1980&auto=format&fit=crop" alt="Baking process">\n                    <p>\n                        Nestled in the heart of Kathmandu, our bakery has been serving freshly baked goods since 1988. We pride ourselves on using organic, locally-sourced ingredients from the Himalayan region to create delicious treats for our community. Our passion is crafting high-quality breads, pastries, and cakes that bring a smile to your face. We believe in tradition, quality, and the simple joy of a warm, freshly baked delight.\n                    </p>\n                </div>\n            </div>\n        </section>\n\n        <section id="menu" class="page-section">\n            <div class="container">\n                <h2>Our Menu</h2>\n                <div class="menu-grid">\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1555507036-ab1f4038808a?q=80&w=2070&auto=format&fit=crop" alt="Croissant">\n                        <h3>Butter Croissant</h3>\n                        <p class="price">Rs. 180</p>\n                    </div>\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1598839952546-6274d7a05942?q=80&w=1974&auto=format&fit=crop" alt="Sourdough Bread">\n                        <h3>Himalayan Sourdough</h3>\n                        <p class="price">Rs. 250</p>\n                    </div>\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1571328003735-2d131888a2a4?q=80&w=1964&auto=format&fit=crop" alt="Chocolate Cake Slice">\n                        <h3>Dark Chocolate Slice</h3>\n                        <p class="price">Rs. 280</p>\n                    </div>\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1507133750040-4a8f570215de?q=80&w=1974&auto=format&fit=crop" alt="Espresso">\n                        <h3>Espresso</h3>\n                        <p class="price">Rs. 150</p>\n                    </div>\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1541167760496-1628856ab772?q=80&w=1937&auto=format&fit=crop" alt="Cappuccino">\n                        <h3>Cappuccino</h3>\n                        <p class="price">Rs. 220</p>\n                    </div>\n                    <div class="menu-item">\n                        <img src="https://images.unsplash.com/photo-1517433674681-1d35a7f454db?q=80&w=2070&auto=format&fit=crop" alt="Latte">\n                        <h3>Cafe Latte</h3>\n                        <p class="price">Rs. 250</p>\n                    </div>\n                </div>\n            </div>\n        </section>\n\n        <section id="contact" class="page-section">\n            <div class="container">\n                <h2>Contact Us</h2>\n                <div class="contact-content">\n                    <div class="contact-info">\n                        <h3>Visit Our Bakery</h3>\n                        <p>123 Bakery Street, Thamel<br>Kathmandu, Nepal</p>\n                        <h3>Opening Hours</h3>\n                        <p>Sun - Sat: 8:00 AM - 9:00 PM</p>\n                        <h3>Get in Touch</h3>\n                        <p>Email: contact@kathmandubakery.com</p>\n                        <p>Phone: +977 1 4412345</p>\n                    </div>\n                    <div class="contact-map">\n                         <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d56516.27689233041!2d85.29111322247194!3d27.70903193352737!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39eb198a307baabf%3A0xb5137c1bf18db1ea!2sKathmandu%2044600%2C%20Nepal!5e0!3m2!1sen!2sus!4v1672852578531!5m2!1sen!2sus" width="100%" height="350" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>\n                    </div>\n                </div>\n            </div>\n        </section>\n    </main>\n\n    <footer>\n        <p>&copy; 2024 Kathmandu Bakery. All Rights Reserved.</p>\n    </footer>\n\n    <script src="script.js"></script>\n</body>\n</html>\n```\n```css\n/* General Body Styles */\n* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n}\n\nhtml {\n    scroll-behavior: smooth;\n}\n\nbody {\n    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;\n    line-height: 1.6;\n    color: #333;\n    background-color: #fdfaf6;\n}\n\n.container {\n    max-width: 1100px;\n    margin: auto;\n    padding: 0 2rem;\n}\n\n/* Header & Navigation */\n.navbar {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n    padding: 1rem 2rem;\n    background-color: #fff;\n    box-shadow: 0 2px 5px rgba(0,0,0,0.1);\n    position: fixed;\n    width: 100%;\n    top: 0;\n    z-index: 1000;\n}\n\n.nav-logo {\n    font-size: 1.5rem;\n    font-weight: bold;\n    color: #5a3e36;\n    text-decoration: none;\n}\n\n.nav-menu {\n    display: flex;\n    list-style: none;\n    gap: 1.5rem;\n}\n\n.nav-link {\n    text-decoration: none;\n    color: #5a3e36;\n    font-weight: 500;\n    transition: color 0.3s ease;\n}\n\n.nav-link:hover {\n    color: #c5a880;\n}\n\n.hamburger {\n    display: none;\n    cursor: pointer;\n}\n\n.bar {\n    display: block;\n    width: 25px;\n    height: 3px;\n    margin: 5px auto;\n    background-color: #5a3e36;\n    transition: all 0.3s ease-in-out;\n}\n\n/* Hero Section */\n.hero {\n    background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(\'https://images.unsplash.com/photo-1509440159596-024908877268?q=80&w=2070&auto=format&fit=crop\') no-repeat center center/cover;\n    height: 100vh;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    text-align: center;\n    color: #fff;\n    padding: 0 1rem;\n}\n\n.hero-content h1 {\n    font-size: 3rem;\n    margin-bottom: 0.5rem;\n}\n\n.hero-content p {\n    font-size: 1.25rem;\n    margin-bottom: 2rem;\n    font-style: italic;\n}\n\n.cta-button {\n    display: inline-block;\n    padding: 0.8rem 1.8rem;\n    background-color: #c5a880;\n    color: #fff;\n    text-decoration: none;\n    border-radius: 5px;\n    font-weight: bold;\n    transition: background-color 0.3s ease;\n}\n\n.cta-button:hover {\n    background-color: #b0916a;\n}\n\n/* Page Sections */\n.page-section {\n    padding: 5rem 0;\n}\n\n.page-section:nth-child(odd) {\n    background-color: #fff;\n}\n\n.page-section h2 {\n    text-align: center;\n    margin-bottom: 3rem;\n    font-size: 2.5rem;\n    color: #5a3e36;\n}\n\n/* About Section */\n.about-content {\n    display: flex;\n    gap: 2rem;\n    align-items: center;\n}\n\n.about-content img {\n    max-width: 45%;\n    border-radius: 8px;\n    box-shadow: 0 4px 8px rgba(0,0,0,0.1);\n}\n\n.about-content p {\n    flex: 1;\n    font-size: 1.1rem;\n}\n\n/* Menu Section */\n.menu-grid {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));\n    gap: 2rem;\n}\n\n.menu-item {\n    background: #fff;\n    border-radius: 8px;\n    box-shadow: 0 4px 10px rgba(0,0,0,0.08);\n    overflow: hidden;\n    text-align: center;\n    transition: transform 0.3s ease;\n}\n\n.menu-item:hover {\n    transform: translateY(-5px);\n}\n\n.menu-item img {\n    width: 100%;\n    height: 200px;\n    object-fit: cover;\n}\n\n.menu-item h3 {\n    margin: 1rem 0 0.5rem;\n    color: #5a3e36;\n}\n\n.menu-item .price {\n    font-weight: bold;\n    color: #c5a880;\n    margin-bottom: 1rem;\n}\n\n/* Contact Section */\n.contact-content {\n    display: flex;\n    gap: 3rem;\n    flex-wrap: wrap;\n}\n\n.contact-info, .contact-map {\n    flex: 1;\n    min-width: 300px;\n}\n\n.contact-info h3 {\n    color: #5a3e36;\n    margin-top: 1.5rem;\n    margin-bottom: 0.5rem;\n}\n\n.contact-info p {\n    margin-bottom: 0.5rem;\n}\n\n.contact-map iframe {\n    border-radius: 8px;\n}\n\n/* Footer */\nfooter {\n    background: #5a3e36;\n    color: #fff;\n    text-align: center;\n    padding: 1.5rem 0;\n}\n\n/* Responsive Design */\n@media (max-width: 768px) {\n    .nav-menu {\n        position: fixed;\n        left: -100%;\n        top: 65px; /* Adjust based on navbar height */\n        flex-direction: column;\n        background-color: #fff;\n        width: 100%;\n        text-align: center;\n        transition: 0.3s;\n        box-shadow: 0 10px 27px rgba(0, 0, 0, 0.05);\n    }\n\n    .nav-menu.active {\n        left: 0;\n    }\n\n    .nav-item {\n        padding: 1.5rem 0;\n    }\n    \n    .nav-link {\n        font-size: 1.2rem;\n    }\n\n    .hamburger {\n        display: block;\n    }\n\n    .hamburger.active .bar:nth-child(2) {\n        opacity: 0;\n    }\n\n    .hamburger.active .bar:nth-child(1) {\n        transform: translateY(8px) rotate(45deg);\n    }\n\n    .hamburger.active .bar:nth-child(3) {\n        transform: translateY(-8px) rotate(-45deg);\n    }\n\n    .hero-content h1 {\n        font-size: 2.5rem;\n    }\n\n    .about-content {\n        flex-direction: column;\n    }\n    \n    .about-content img {\n        max-width: 100%;\n    }\n}\n```\n```javascript\nconst hamburger = document.querySelector(".hamburger");\nconst navMenu = document.querySelector(".nav-menu");\nconst navLinks = document.querySelectorAll(".nav-link");\n\n// Toggle mobile menu\nhamburger.addEventListener("click", () => {\n    hamburger.classList.toggle("active");\n    navMenu.classList.toggle("active");\n});\n\n// Close mobile menu when a link is clicked\nnavLinks.forEach(n => n.addEventListener("click", closeMenu));\n\nfunction closeMenu() {\n    hamburger.classList.remove("active");\n    navMenu.classList.remove("active");\n}\n\n// Close mobile menu when clicking outside\ndocument.addEventListener(\'click\', (event) => {\n    const isClickInsideMenu = navMenu.contains(event.target);\n    const isClickOnHamburger = hamburger.contains(event.target);\n    if (!isClickInsideMenu && !isClickOnHamburger && navMenu.classList.contains(\'active\')) {\n        closeMenu();\n    }\n});\n```'