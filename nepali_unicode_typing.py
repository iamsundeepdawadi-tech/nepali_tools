# https://www.thapaliya.com/en/writings/practice-romanized-nepali-unicode-in-your-browser/

import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

# --- HELPER FUNCTION TO EMBED THE IMAGE ---
def image_to_base64_string(path):
    """Reads an image file and returns it as a base64 encoded string."""
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(
            f"Image file not found at '{path}'. "
            "Please ensure 'nepali_keyboard_layout.png' is in the same directory as this script."
        )
        return None

# --- JAVASCRIPT INJECTION FOR THE KEYBOARD ---
def inject_custom_keyboard():
    """
    Injects the JavaScript code to handle the Nepali keyboard conversion.
    This uses the robust input-based conversion logic combined with the direct key mapping.
    """
    component_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <script>
            // This is the direct, one-to-one mapping from a QWERTY key to a Nepali character.
            // prettier-ignore
            const keyToNep = {
              "a": "\\u093E", "b": "\\u092C", "c": "\\u091B", "d": "\\u0926", "e": "\\u0947",
              "f": "\\u0909", "g": "\\u0917", "h": "\\u0939", "i": "\\u093F", "j": "\\u091C",
              "k": "\\u0915", "l": "\\u0932", "m": "\\u092E", "n": "\\u0928", "o": "\\u094B",
              "p": "\\u092A", "q": "\\u091F", "r": "\\u0930", "s": "\\u0938", "t": "\\u0924",
              "u": "\\u0941", "v": "\\u0935", "w": "\\u094C", "x": "\\u0921", "y": "\\u092F",
              "z": "\\u0937",
              "A": "\\u0906", "B": "\\u092D", "C": "\\u091A", "D": "\\u0927", "E": "\\u0948",
              "F": "\\u090A", "G": "\\u0918", "H": "\\u0905", "I": "\\u0940", "J": "\\u091D",
              "K": "\\u0916", "L": "\\u0933", "M": "\\u0902", "N": "\\u0923", "O": "\\u0913",
              "P": "\\u092B", "Q": "\\u0920", "R": "\\u0943", "S": "\\u0936", "T": "\\u0925",
              "U": "\\u0942", "V": "\\u0901", "W": "\\u0914", "X": "\\u0922", "Y": "\\u091E",
              "Z": "\\u090B",
              "0": "\\u0966", "1": "\\u0967", "2": "\\u0968", "3": "\\u0969", "4": "\\u096A",
              "5": "\\u096B", "6": "\\u096C", "7": "\\u096D", "8": "\\u096E", "9": "\\u096F",
              "`": "\\u093D", "~": "\\u093C", "_": "\\u0952", "+": "\\u200C", "=": "\\u200D",
              "[": "\\u0907", "{": "\\u0908", "]": "\\u090F", "}": "\\u0910",
              "\\\\": "\\u0950", "|": "\\u0903", "<": "\\u0919", ".": "\\u0964", ">": "\\u0965",
              "/": "\\u094D", "?": "?"
            };

            // This function converts an entire string of Roman characters to Nepali.
            function romanToNepali(romanText) {
                if (!romanText) return '';
                let nepaliText = '';
                for (let i = 0; i < romanText.length; i++) {
                    const char = romanText[i];
                    // Append the mapped Nepali character, or the original character if no mapping exists.
                    nepaliText += keyToNep[char] || char;
                }
                return nepaliText;
            }

            // This function finds all text areas and attaches the conversion logic.
            function setupNepaliTyping() {
                const textAreas = parent.document.querySelectorAll('textarea');
                
                textAreas.forEach(textarea => {
                    // Check if the logic is already attached to prevent duplicates.
                    if (textarea.hasAttribute('data-nepali-enabled')) return;
                    textarea.setAttribute('data-nepali-enabled', 'true');
                    
                    let isConverting = false;
                    
                    // The 'input' event is robust and fires on typing, pasting, etc.
                    textarea.addEventListener('input', function(e) {
                        if (isConverting) return; // Prevent recursive event loops.
                        
                        isConverting = true;
                        
                        const originalValue = this.value;
                        const cursorPos = this.selectionStart;
                        
                        // Convert the entire text content.
                        const nepaliText = romanToNepali(originalValue);
                        
                        // Only update the DOM if the text has actually changed.
                        if (nepaliText !== originalValue) {
                            this.value = nepaliText;
                            
                            // Restore the cursor to its correct position.
                            this.selectionStart = this.selectionEnd = cursorPos;
                            
                            // IMPORTANT: Dispatch a new 'input' event to notify Streamlit
                            // that the value has changed programmatically.
                            this.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                        
                        isConverting = false;
                    });
                });
            }

            // Run the setup function on initial load.
            setupNepaliTyping();
            
            // Use a MutationObserver to re-apply the logic if Streamlit re-renders the DOM.
            // This makes the keyboard integration very robust.
            const observer = new MutationObserver(function() {
                setupNepaliTyping();
            });
            
            observer.observe(parent.document.body, {
                childList: true,
                subtree: true
            });
        </script>
    </body>
    </html>
    """
    components.html(component_html, height=0)

# --- MAIN STREAMLIT APPLICATION ---
def main():
    """The main function that runs the Streamlit app."""
    st.set_page_config(
        page_title="Nepali Romanized Keyboard",
        page_icon="🇳🇵",
        layout="centered"
    )

    # Use session_state to manage the visibility of the keyboard layout popup.
    if "show_keyboard" not in st.session_state:
        st.session_state.show_keyboard = False

    st.title("🇳🇵 Nepali Romanized Typing")
    st.write("Type using a standard English (QWERTY) keyboard to write in Nepali. The conversion happens instantly.")
    
    # The text area where the user types.
    st.text_area(
        "Type here:",
        key="nepali_input_area", # A unique key for our JavaScript to find the element.
        height=200,
        placeholder="नमस्ते! यहाँ टाइप गर्न सुरु गर्नुहोस्... (Namaste! Start typing here...)"
    )

    # Button to show or hide the keyboard layout image.
    if st.button("Show Keyboard Layout", use_container_width=True):
        st.session_state.show_keyboard = not st.session_state.show_keyboard

    # This block conditionally displays the keyboard layout image.
    if st.session_state.show_keyboard:
        # Construct the path to the image and convert it to a base64 string.
        image_path = Path(__file__).parent / "romanized-nepali-unicode-keyboard-layout.png"
        keyboard_image_b64 = image_to_base64_string(image_path)
        
        if keyboard_image_b64:
            with st.container(border=True):
                # Display the image.
                # FIX: Replaced deprecated `use_column_width=True` with `use_column_width='auto'`.
                st.image(
                    f"data:image/png;base64,{keyboard_image_b64}",
                    caption="Nepali Romanized Keyboard Layout",
                    use_column_width='auto', 
                )
                # Button to hide the layout.
                if st.button("Hide Keyboard Layout", use_container_width=True):
                    st.session_state.show_keyboard = False
                    st.rerun() # Rerun to immediately reflect the change.

    # Finally, inject the JavaScript that makes the keyboard work.
    inject_custom_keyboard()


if __name__ == "__main__":
    main()