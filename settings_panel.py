"""
Interactive settings panel generator for bilingual EPUBs.

This module creates an embeddable HTML/CSS/JavaScript settings widget
that allows readers to customize the EPUB appearance in real-time.
"""


def generate_settings_panel(config):
    """
    Generates a simple gray card with settings gear icon.
    
    Args:
        config: Configuration dict with 'bilingual' key containing BilingualConfig
        
    Returns:
        String containing HTML for the settings card
    """
    bilingual_config = config.get('bilingual')
    if not bilingual_config:
        return ""
    
    from bilingual_config import LayoutMode, StyleMode
    
    # Get current defaults
    default_layout = bilingual_config.layout_mode.value
    default_en_color = bilingual_config.original_color or '#000000'
    default_es_color = bilingual_config.translation_color or '#666666'
    default_column_gap = bilingual_config.column_gap_percentage
    
    settings_html = f'''
<!-- Reading Settings Card -->
<div class="reading-settings-card">
    <button id="settings-toggle" class="settings-icon-btn" title="Reading Settings">
        ⚙️
    </button>
    <span class="settings-label">Reading Settings</span>
</div>

<!-- Settings Panel (Hidden by default) -->
<div id="settings-panel" class="settings-panel" style="display: none;">
    <div class="settings-header">
        <h3>Reading Settings</h3>
        <button id="close-settings" class="close-btn">×</button>
    </div>
    
    <div class="settings-body">
        <div class="setting-item">
            <label>Layout Mode:</label>
            <select id="layout-mode">
                <option value="below" {'selected' if default_layout == 'below' else ''}>Spanish Below</option>
                <option value="above" {'selected' if default_layout == 'above' else ''}>Spanish Above</option>
                <option value="side" {'selected' if default_layout == 'side' else ''}>Side-by-Side</option>
                <option value="only" {'selected' if default_layout == 'only' else ''}>Spanish Only</option>
            </select>
        </div>
        
        <div class="setting-item">
            <label>English Color:</label>
            <input type="color" id="en-color" value="{default_en_color}">
        </div>
        
        <div class="setting-item">
            <label>Spanish Color:</label>
            <input type="color" id="es-color" value="{default_es_color}">
        </div>
        
        <div class="setting-item">
            <label>Font Size:</label>
            <select id="font-size">
                <option value="0.9em">Small</option>
                <option value="1em" selected>Normal</option>
                <option value="1.1em">Large</option>
            </select>
        </div>
        
        <div class="settings-footer">
            <button id="reset-settings" class="reset-btn">Reset</button>
            <button id="apply-settings" class="apply-btn">Apply</button>
        </div>
    </div>
</div>

<style>
/* Gray Settings Card at Top */
.reading-settings-card {{
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 12px 20px;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}}

.settings-icon-btn {{
    background: #888;
    color: white;
    border: none;
    border-radius: 6px;
    width: 40px;
    height: 40px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}}

.settings-icon-btn:hover {{
    background: #666;
}}

.settings-label {{
    color: #666;
    font-size: 14px;
    font-weight: 500;
}}

/* Settings Panel */
.settings-panel {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    width: 90%;
    max-width: 400px;
    z-index: 10000;
}}

.settings-header {{
    background: #888;
    color: white;
    padding: 15px 20px;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.settings-header h3 {{
    margin: 0;
    font-size: 16px;
}}

.close-btn {{
    background: transparent;
    border: none;
    color: white;
    font-size: 28px;
    cursor: pointer;
    padding: 0;
    width: 30px;
    height: 30px;
    line-height: 1;
}}

.settings-body {{
    padding: 20px;
}}

.setting-item {{
    margin-bottom: 15px;
}}

.setting-item label {{
    display: block;
    margin-bottom: 6px;
    font-size: 14px;
    color: #333;
}}

.setting-item select,
.setting-item input[type="color"] {{
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 6px;
}}

.settings-footer {{
    display: flex;
    gap: 10px;
    margin-top: 20px;
}}

.reset-btn,
.apply-btn {{
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}}

.reset-btn {{
    background: #f5f5f5;
    color: #666;
}}

.apply-btn {{
    background: #888;
    color: white;
}}

.apply-btn:hover {{
    background: #666;
}}

#settings-backdrop {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 9999;
    display: none;
}}
</style>

<div id="settings-backdrop"></div>

<script>
(function() {{
    const DEFAULTS = {{
        layoutMode: '{default_layout}',
        enColor: '{default_en_color}',
        esColor: '{default_es_color}',
        fontSize: '1em'
    }};
    
    function loadSettings() {{
        const saved = localStorage.getItem('bilingualSettings');
        return saved ? JSON.parse(saved) : DEFAULTS;
    }}
    
    function saveSettings(settings) {{
        localStorage.setItem('bilingualSettings', JSON.stringify(settings));
    }}
    
    function applySettings(settings) {{
        document.querySelectorAll('body > *:not(.reading-settings-card):not(#settings-panel):not(#settings-backdrop)').forEach(el => {{
            if (!el.classList.contains('es-translation') && !el.classList.contains('es-trans')) {{
                el.style.color = settings.enColor;
            }}
        }});
        
        document.querySelectorAll('.es-translation, .es-trans').forEach(el => {{
            el.style.color = settings.esColor;
        }});
        
        document.body.style.fontSize = settings.fontSize;
    }}
    
    document.addEventListener('DOMContentLoaded', function() {{
        const panel = document.getElementById('settings-panel');
        const backdrop = document.getElementById('settings-backdrop');
        const toggleBtn = document.getElementById('settings-toggle');
        const closeBtn = document.getElementById('close-settings');
        const applyBtn = document.getElementById('apply-settings');
        const resetBtn = document.getElementById('reset-settings');
        
        const settings = loadSettings();
        applySettings(settings);
        
        toggleBtn.addEventListener('click', function() {{
            panel.style.display = 'block';
            backdrop.style.display = 'block';
        }});
        
        function closePanel() {{
            panel.style.display = 'none';
            backdrop.style.display = 'none';
        }}
        
        closeBtn.addEventListener('click', closePanel);
        backdrop.addEventListener('click', closePanel);
        
        applyBtn.addEventListener('click', function() {{
            const newSettings = {{
                layoutMode: document.getElementById('layout-mode').value,
                enColor: document.getElementById('en-color').value,
                esColor: document.getElementById('es-color').value,
                fontSize: document.getElementById('font-size').value
            }};
            
            saveSettings(newSettings);
            applySettings(newSettings);
            closePanel();
        }});
        
        resetBtn.addEventListener('click', function() {{
            if (confirm('Reset settings?')) {{
                localStorage.removeItem('bilingualSettings');
                location.reload();
            }}
        }});
    }});
}})();
</script>
'''
    
    return settings_html

    """
    Generates the HTML, CSS, and JavaScript for an interactive settings panel.
    
    Args:
        config: Configuration dict with 'bilingual' key containing BilingualConfig
        
    Returns:
        String containing complete HTML for the settings panel
    """
    bilingual_config = config.get('bilingual')
    if not bilingual_config:
        return ""
    
    from bilingual_config import LayoutMode, StyleMode
    
    # Get current defaults
    default_layout = bilingual_config.layout_mode.value
    default_en_color = bilingual_config.original_color or '#000000'
    default_es_color = bilingual_config.translation_color or '#666666'
    default_column_gap = bilingual_config.column_gap_percentage
    
    settings_html = f'''
<!-- Bilingual Reading Settings Panel -->
<div id="bilingual-settings-panel" style="display: none;">
    <div class="settings-header">
        <h3>⚙️ Reading Settings</h3>
        <button id="close-settings" class="close-btn">✕</button>
    </div>
    
    <div class="settings-content">
        <div class="setting-group">
            <label for="layout-mode">Layout Mode:</label>
            <select id="layout-mode">
                <option value="below" {'selected' if default_layout == 'below' else ''}>Spanish Below English</option>
                <option value="above" {'selected' if default_layout == 'above' else ''}>Spanish Above English</option>
                <option value="side" {'selected' if default_layout == 'side' else ''}>Side-by-Side</option>
                <option value="only" {'selected' if default_layout == 'only' else ''}>Spanish Only</option>
            </select>
        </div>
        
        <div class="setting-group">
            <label for="en-color">English Text Color:</label>
            <input type="color" id="en-color" value="{default_en_color}">
            <input type="text" id="en-color-text" value="{default_en_color}" placeholder="#000000">
        </div>
        
        <div class="setting-group">
            <label for="es-color">Spanish Text Color:</label>
            <input type="color" id="es-color" value="{default_es_color}">
            <input type="text" id="es-color-text" value="{default_es_color}" placeholder="#666666">
        </div>
        
        <div class="setting-group" id="column-gap-group" style="{'display: block;' if default_layout == 'side' else 'display: none;'}">
            <label for="column-gap">Column Gap: <span id="gap-value">{default_column_gap}%</span></label>
            <input type="range" id="column-gap" min="5" max="30" value="{default_column_gap}">
        </div>
        
        <div class="setting-group">
            <label for="font-size">Font Size:</label>
            <select id="font-size">
                <option value="0.9em">Small</option>
                <option value="1em" selected>Normal</option>
                <option value="1.1em">Large</option>
                <option value="1.2em">Extra Large</option>
            </select>
        </div>
        
        <div class="setting-group">
            <label>
                <input type="checkbox" id="bold-spanish">
                <span>Bold Spanish Text</span>
            </label>
        </div>
    </div>
    
    <div class="settings-footer">
        <button id="reset-settings" class="reset-btn">Reset to Defaults</button>
        <button id="apply-settings" class="apply-btn">Apply Changes</button>
    </div>
</div>

<button id="settings-toggle" class="settings-toggle" title="Reading Settings">
    ⚙️
</button>

<style>
/* Settings Toggle Button */
.settings-toggle {{
    position: fixed;
    top: 10px;
    right: 10px;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    font-size: 22px;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    z-index: 9999;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.settings-toggle:hover {{
    transform: scale(1.1) rotate(90deg);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
}}

.settings-toggle:active {{
    transform: scale(0.95);
}}

/* Settings Panel */
#bilingual-settings-panel {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 450px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    animation: slideIn 0.3s ease-out;
}}

@keyframes slideIn {{
    from {{
        opacity: 0;
        transform: translate(-50%, -40%);
    }}
    to {{
        opacity: 1;
        transform: translate(-50%, -50%);
    }}
}}

.settings-header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 20px;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.settings-header h3 {{
    margin: 0;
    font-size: 18px;
    font-weight: 600;
}}

.close-btn {{
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    font-size: 24px;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}}

.close-btn:hover {{
    background: rgba(255, 255, 255, 0.3);
}}

.settings-content {{
    padding: 20px;
    max-height: 60vh;
    overflow-y: auto;
}}

.setting-group {{
    margin-bottom: 18px;
}}

.setting-group label {{
    display: block;
    font-weight: 500;
    margin-bottom: 6px;
    color: #333;
    font-size: 14px;
}}

.setting-group select,
.setting-group input[type="text"],
.setting-group input[type="range"] {{
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    transition: border-color 0.2s;
}}

.setting-group select:focus,
.setting-group input[type="text"]:focus {{
    outline: none;
    border-color: #667eea;
}}

.setting-group input[type="color"] {{
    width: 60px;
    height: 40px;
    border: 1px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
    margin-right: 10px;
}}

.setting-group input[type="text"] {{
    display: inline-block;
    width: calc(100% - 80px);
}}

.setting-group input[type="checkbox"] {{
    margin-right: 8px;
    width: 18px;
    height: 18px;
    cursor: pointer;
}}

.setting-group input[type="range"] {{
    padding: 0;
}}

.settings-footer {{
    padding: 16px 20px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
    justify-content: space-between;
}}

.reset-btn,
.apply-btn {{
    flex: 1;
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}}

.reset-btn {{
    background: #f5f5f5;
    color: #666;
}}

.reset-btn:hover {{
    background: #e0e0e0;
}}

.apply-btn {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}}

.apply-btn:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}}

/* Overlay backdrop */
#settings-backdrop {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 9998;
    display: none;
}}
</style>

<div id="settings-backdrop"></div>

<script>
(function() {{
    'use strict';
    
    // Default settings
    const DEFAULTS = {{
        layoutMode: '{default_layout}',
        enColor: '{default_en_color}',
        esColor: '{default_es_color}',
        columnGap: {default_column_gap},
        fontSize: '1em',
        boldSpanish: false
    }};
    
    // Load settings from localStorage
    function loadSettings() {{
        const saved = localStorage.getItem('bilingualSettings');
        return saved ? JSON.parse(saved) : DEFAULTS;
    }}
    
    // Save settings to localStorage
    function saveSettings(settings) {{
        localStorage.setItem('bilingualSettings', JSON.stringify(settings));
    }}
    
    // Apply settings to the page
    function applySettings(settings) {{
        const root = document.documentElement;
        
        // Apply colors via CSS variables
        root.style.setProperty('--en-color', settings.enColor);
        root.style.setProperty('--es-color', settings.esColor);
        root.style.setProperty('--font-size', settings.fontSize);
        root.style.setProperty('--es-weight', settings.boldSpanish ? 'bold' : 'normal');
        
        // Update all English text
        document.querySelectorAll('body > *:not(#bilingual-settings-panel):not(#settings-backdrop):not(.settings-toggle)').forEach(el => {{
            if (!el.classList.contains('es-translation') && !el.classList.contains('es-trans')) {{
                el.style.color = settings.enColor;
            }}
        }});
        
        // Update all Spanish text
        document.querySelectorAll('.es-translation, .es-trans, span[class*="es-"]').forEach(el => {{
            el.style.color = settings.esColor;
            el.style.fontWeight = settings.boldSpanish ? 'bold' : 'normal';
        }});
        
        // Apply font size
        document.body.style.fontSize = settings.fontSize;
        
        // Handle column gap for side-by-side mode (if applicable)
        if (settings.layoutMode === 'side') {{
            document.querySelectorAll('table[width="100%"] td').forEach((td, index) => {{
                if (index % 3 === 1) {{ // Middle gap column
                    td.setAttribute('width', settings.columnGap + '%');
                }}
            }});
        }}
        
        console.log('Settings applied:', settings);
    }}
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {{
        const panel = document.getElementById('bilingual-settings-panel');
        const backdrop = document.getElementById('settings-backdrop');
        const toggleBtn = document.getElementById('settings-toggle');
        const closeBtn = document.getElementById('close-settings');
        const applyBtn = document.getElementById('apply-settings');
        const resetBtn = document.getElementById('reset-settings');
        
        // Load and apply saved settings
        const settings = loadSettings();
        applySettings(settings);
        
        // Populate form with current settings
        document.getElementById('layout-mode').value = settings.layoutMode;
        document.getElementById('en-color').value = settings.enColor;
        document.getElementById('en-color-text').value = settings.enColor;
        document.getElementById('es-color').value = settings.esColor;
        document.getElementById('es-color-text').value = settings.esColor;
        document.getElementById('column-gap').value = settings.columnGap;
        document.getElementById('gap-value').textContent = settings.columnGap + '%';
        document.getElementById('font-size').value = settings.fontSize;
        document.getElementById('bold-spanish').checked = settings.boldSpanish;
        
        // Toggle panel
        function showPanel() {{
            panel.style.display = 'block';
            backdrop.style.display = 'block';
        }}
        
        function hidePanel() {{
            panel.style.display = 'none';
            backdrop.style.display = 'none';
        }}
        
        toggleBtn.addEventListener('click', showPanel);
        closeBtn.addEventListener('click', hidePanel);
        backdrop.addEventListener('click', hidePanel);
        
        // Color picker sync
        document.getElementById('en-color').addEventListener('input', function() {{
            document.getElementById('en-color-text').value = this.value;
        }});
        
        document.getElementById('es-color').addEventListener('input', function() {{
            document.getElementById('es-color-text').value = this.value;
        }});
        
        document.getElementById('en-color-text').addEventListener('input', function() {{
            if (/^#[0-9A-F]{{6}}$/i.test(this.value)) {{
                document.getElementById('en-color').value = this.value;
            }}
        }});
        
        document.getElementById('es-color-text').addEventListener('input', function() {{
            if (/^#[0-9A-F]{{6}}$/i.test(this.value)) {{
                document.getElementById('es-color').value = this.value;
            }}
        }});
        
        // Column gap slider
        document.getElementById('column-gap').addEventListener('input', function() {{
            document.getElementById('gap-value').textContent = this.value + '%';
        }});
        
        // Show/hide column gap based on layout mode
        document.getElementById('layout-mode').addEventListener('change', function() {{
            const gapGroup = document.getElementById('column-gap-group');
            gapGroup.style.display = this.value === 'side' ? 'block' : 'none';
        }});
        
        // Apply settings
        applyBtn.addEventListener('click', function() {{
            const newSettings = {{
                layoutMode: document.getElementById('layout-mode').value,
                enColor: document.getElementById('en-color').value,
                esColor: document.getElementById('es-color').value,
                columnGap: parseInt(document.getElementById('column-gap').value),
                fontSize: document.getElementById('font-size').value,
                boldSpanish: document.getElementById('bold-spanish').checked
            }};
            
            saveSettings(newSettings);
            applySettings(newSettings);
            hidePanel();
            
            // Show confirmation
            const btn = this;
            const originalText = btn.textContent;
            btn.textContent = '✓ Applied!';
            btn.style.background = '#10b981';
            setTimeout(() => {{
                btn.textContent = originalText;
                btn.style.background = '';
            }}, 2000);
        }});
        
        // Reset settings
        resetBtn.addEventListener('click', function() {{
            if (confirm('Reset all settings to defaults?')) {{
                localStorage.removeItem('bilingualSettings');
                applySettings(DEFAULTS);
                location.reload();
            }}
        }});
    }});
}})();
</script>
'''
    
    return settings_html
