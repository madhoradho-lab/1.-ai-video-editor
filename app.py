                    if os.path.exists(concat_list_path): os.remove(concat_list_path)

                    st.success("🏁 Pro-Level Video Rendered with Enhanced Crisp Studio Audio!")
                    st.video(final_render_path)
                    
                    with open(final_render_path, "rb") as video_file:
                        st.download_button(
                            label="📥 Download Your Pro Edited Video File",
                            data=video_file.read(),
                            file_name="pro_share_market_output.mp4",
                            mime="video/mp4"
                        )
                except Exception as render_err:
                    st.error(f"Render Error: {str(render_err)}")
