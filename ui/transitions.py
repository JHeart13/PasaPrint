import streamlit as st


def load_transition_styles():
    st.markdown(
        """
        <style>
        @keyframes ppPageEnter {
            0% {
                opacity: 0;
                transform: translateY(12px);
                filter: brightness(1.08);
            }

            100% {
                opacity: 1;
                transform: translateY(0);
                filter: brightness(1);
            }
        }

        [class*="st-key-pp-page-"] {
            animation: ppPageEnter 0.4s ease-out both;
        }

        @media (prefers-reduced-motion: reduce) {
            [class*="st-key-pp-page-"] {
                animation: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )