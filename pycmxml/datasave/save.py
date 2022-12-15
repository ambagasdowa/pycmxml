
import utils.utils as lib
# UIX
from rich import print
from rich.progress import track
from rich.progress import Progress

from datetime import datetime, date, tzinfo, timedelta
import time


# === === === === === === === ===  remolques  === === === === === === === ===
def indb(api, cfdi, cursor, tree, ns, cmex_api_controls_files_id, created, modified, status, element_qry, mod_element, init, offset, step, namespace):

    # init = 18
    # offset = 0 # the normal is zero
    # step = 0
    # namespace = "tipos_figura"
    #    cfdi_data = ''
 #   api = True
    if(mod_element != ''):
        query_element = mod_element
    else:
        query_element = "select id,cmex_api_tagname from sistemas.dbo.cmex_api_tags where cmex_api_section_id = ?"

    if (api == True):
        # Get the fields for identificacion element
        element_id = init + offset  # identificacion
        offset = offset + step
        print("[red] element_id : "+str(element_id)+"[red]")

        cursor.execute(query_element, (element_id,))
        elements = cursor.fetchall()

        for ids, ele in elements:
            print("[red]"+str(ids)+"[red] : [blue]"+str(ele)+"[blue]")

        for i in track(range(2), description="Saving to "+lib.camelize(namespace)+" data to database..."):
            time.sleep(1)  # Simulate work being done

#        save_query = ()
        for query_id, name in elements:
            saved_query = (cmex_api_controls_files_id, element_id, query_id,
                           cfdi[name], created, modified, status,)
            cursor.execute(element_qry, saved_query)
            cursor.commit()

    else:
        print('[cyan]Go inside '+lib.camelize(namespace)+' :[cyan]')
        for concept in tree.findall('.//cartapore20:' + lib.camelize(namespace), ns):
            print(concept.attrib)

            # Get the fields for identificacion element
            element_id = init + offset  # identificacion
            offset = offset + step
            print("[red] element_id : "+str(element_id)+"[red]")

            query_element = "select id,cmex_api_tagname from sistemas.dbo.cmex_api_tags where cmex_api_section_id = ?"
            cursor.execute(query_element, (element_id,))

            elements = cursor.fetchall()

            for ids, ele in elements:
                print("[red]"+str(ids)+"[red] : [blue]"+str(ele)+"[blue]")

            for i in track(range(2), description="Saving to "+lib.camelize(namespace)+" data to database..."):
                time.sleep(1)  # Simulate work being done

 #           save_query = ()
            for query_id, name in elements:
                if lib.camelize(name) in concept.attrib:
                    saved_query = (cmex_api_controls_files_id, element_id, query_id,
                                   concept.attrib[lib.camelize(name)], created, modified, status,)
                    cursor.execute(element_qry, saved_query)
                    cursor.commit()

        # === === === === === === === ===  Traslados === === === === === === === ===
