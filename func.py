from bs4 import BeautifulSoup
import re, urllib.request, json, io, oci
from urllib.request import Request, urlopen
from urllib.error import URLError
from fdk import response

link = 'https://forms.rbwm.gov.uk/bincollections?uprn=0000000000000000000000' #Insert the bin collection date page you wish to scrap

def get_dates():
    #req = allKeyValuesString
    req = Request(link)
    try:
        with urllib.request.urlopen(req) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        result, recycling, refuse = ([] for i in range(3))

        for row in soup.find_all('tr'):
            for cell in row.find_all('td'):
                if re.search("Recycling", cell.get_text()):
                    recycling.append(row.find_all('td')[1].get_text())
                if re.search("Refuse", cell.get_text()):
                    refuse.append(row.find_all('td')[1].get_text())

        final = {
                "recycling": {"date": recycling},
                "refuse": {"date": refuse},
                }

        return final

    except URLError as e:
        if hasattr(e, 'reason'):
            return f"We failed to reach a server, Reason: {e.reason}"
        elif hasattr(e, 'code'):
            return f"The server could not fulfill the request... Error code: {e.code}"

def send_msg(signer, dates):
    client = oci.ons.NotificationDataPlaneClient(config={}, signer=signer)
    msg = oci.ons.models.MessageDetails(
        body = json.dumps(dates, indent=4),
        title = 'BINS COLLECTION DATES'
    )
    client.publish_message(topic_id = 'ocid1.onstopic.oc1.uk-london-1.xyz', message_details = msg)

def send_msg_to_queue(signer, dates):
    client = oci.queue.QueueClient(config={}, signer=signer, service_endpoint='https://cell-1.queue.messaging.uk-london-1.oci.oraclecloud.com')
    ####
    queue_id = 'ocid1.queue.oc1.uk-london-1.xyz'
    messages = []
    messages.append(oci.queue.models.PutMessagesDetailsEntry(content=json.dumps(dates, indent=4)))
    put_messages_details = oci.queue.models.PutMessagesDetails(messages=messages)
    client.put_messages(queue_id, put_messages_details=put_messages_details)
    ###


def handler(ctx, data: io.BytesIO = None):
    signer = oci.auth.signers.get_resource_principals_signer()
    allKeyValuesString = ""
    cfg = ctx.Config()
    allKeyValuesString += cfg.get("key1", "missing") + " "

    get_dates_resp = get_dates()
    #send_msg(signer, get_dates_resp)

    ####
    send_msg_to_queue(signer, get_dates_resp)
    ####

    return response.Response(ctx,
    response_data=json.dumps({"response": get_dates_resp}),
    headers={"Content-Type": "application/json"}
    )
