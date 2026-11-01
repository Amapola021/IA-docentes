                    pdf.set_fill_color(245, 245, 245)
                    pdf.cell(0, 8, f" REGISTRO DE ASISTENCIA: Inasistencias en el período: [ {inasistencias} ]", ln=True, fill=True, border=1)
                    pdf.ln(5)
                    
                    pdf.multi_cell(0, 6, cuerpo_anonimizado)
                    
                    # BLOQUE DE TRES FIRMAS COMPACTO
                    pdf.ln(15)
                    pos_y = pdf.get_y()
                    if pos_y > 220:
                        pdf.add_page()
                        pos_y = pdf.get_y() + 10
                    
                    pdf.set_xy(15, pos_y)
                    pdf.cell(75, 0, '', 'T')
                    pdf.set_xy(15, pos_y + 1)
                    pdf.cell(75, 4, 'Firma de la Docente', align='C')
                    
                    pdf.set_xy(120, pos_y)
                    pdf.cell(75, 0, '', 'T')
                    pdf.set_xy(120, pos_y + 1)
                    pdf.cell(75, 4, 'Firma Equipo Directivo', ln=True, align='C')
                    
                    pdf.ln(15)
                    pos_y_resp = pdf.get_y()
                    pdf.set_xy(67, pos_y_resp)
                    pdf.cell(75, 0, '', 'T')
                    pdf.set_xy(67, pos_y_resp + 1)
                    pdf.cell(75, 4, 'Firma Adulto Responsable', ln=True, align='C')
                    
                    # GUARDADO Y DESCARGA
                    if not os.path.exists("generado"):
                        os.makedirs("generado")
                        
                    ruta_pdf = "generado/informe_bandeja_inicial.pdf"
                    pdf.output(ruta_pdf)
                    
                    st.success("¡Informe integral generado con éxito!")
                    st.subheader("👀 Vista previa del texto")
                    st.text_area("Texto redactado:", value=cuerpo_anonimizado, height=250)
                    
                    with open(ruta_pdf, "rb") as archivo_pdf:
                        st.download_button(label="📥 Descargar Informe Oficial en PDF", data=archivo_pdf, file_name="Informe_Trayectoria_Escolar.pdf", mime="application/pdf")
                    
                    st.session_state.informes_generados += 1
                    disponibles = limite_actual - st.session_state.informes_generados
                    st.info(f"💡 Te quedan {disponibles} informes disponibles.")
                
                except Exception as e:
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        st.error("🚨 El sistema está procesando muchos informes en este momento.")
                        st.info("⏳ Por favor, espera 30 segundos y vuelve a hacer clic en el botón.")
                    else:
                        st.error(f"🚨 Error al procesar: {e}")
